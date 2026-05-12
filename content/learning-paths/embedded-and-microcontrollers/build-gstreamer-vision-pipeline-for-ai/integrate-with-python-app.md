---
title: Integrate with python application
weight: 5

### FIXED, DO NOT MODIFY
layout: learningpathall
---

## Integrate inference events with a basic Python app

In this step, you will build a small FastAPI dashboard that starts your pipeline, reads `ampcomm` events, and shows live detections in a browser. This gives you a cleaner single-command workflow than running the app and pipeline separately. This example will use the Raspberry Pi CPU, but if you hasve completed the optional step to create a pipeline utilizing Hailo, you can make the same small changes to the pipeline we create here, and run the app pipeline on Hailo as well.

## Use ampcomm for programmatic output

The `ampcomm` stage is the bridge between inference and your application logic. It emits structured detection records (NDJSON) that your Python app can read, filter, and turn into decisions. NDJSON means Newline-Delimited JSON. It is a text format where each line is one complete JSON object. That makes it easy to stream, append to a file, or process line by line.

For sink choice, you have two valid modes:

- `ampsink`: useful during debugging because you can visually inspect what the pipeline is seeing.
- `fakesink`: may be preferred for final programmatic inference because it removes rendering and browser-output overhead, keeps the pipeline simpler, and focuses compute on inference plus event generation.

In this step, the provided JSON defaults to `fakesink` with `ampcomm`. However you can change this to `ampsink` for debugging.

`amposd` controls on-frame overlays such as boxes and labels. Keep it enabled when you need visual debugging. Disable it when you only need programmatic events and want a cleaner, lower-overhead path. Again it is disabled here as it is not required for the app, but can be enabled easily for debugging.

Run this command to overwrite `/work/config/pipelines/05-custom-detector.json` for programmatic output:

```bash
cat > /work/config/pipelines/05-custom-detector.json <<'EOF'
{
	"description": "Custom YOLOv8n ONNX detector with programmatic output.",
	"pipeline": [
		"v4l2src device=/dev/video0 !",
		"videoconvert ! video/x-raw,format=BGRA !",
		"ampinfer opchain-path=/work/config/models/custom-detector/opchain.json active=true !",
		"amptracker content-type=genericObject !",
		"amposd enabled=false !",
		"ampcomm method=file file-name=/work/data/output/custom-detector.ndjson !",
		"fakesink sync=false"
	]
}
EOF
```

Run a dry run to confirm the pipeline expands correctly:

```bash
./tools/amp-menu -p 05-custom-detector
```

Your output should appear as follows:

```output
INSERT OUTPUT HERE - TODO
```

## Create a FastAPI dashboard app

Install FastAPI and Uvicorn in your existing environment:

```bash
python -m pip install fastapi uvicorn
```

Create the app in `/work/apps` using one command. The app does six things:

- Launches `./tools/amp-menu 05-custom-detector` as a child process.
- Tails `/work/data/output/custom-detector.ndjson`.
- Tracks frame-level label presence and keeps recent detections for visibility.
- Applies an misplaced-item policy rule with hold-time behavior.
- Exposes a right-zone status indicator and policy alerts.
- Serves a live dashboard at `http://localhost:8010` by default.

This rule is an intentionally simple example: if a `cup` remains in a right-side "misplaced" zone for a short hold period, an alert is created. When the `cup` is either removed from the frame or moved onto the left-side "approved" zone, the alert is removed. The same pattern can be adapted and extended to restricted-zone monitoring, occupancy thresholds, or other production policies.

The sample code also includes a coordinate fallback path so the policy still works when a stream provides normalized box coordinates but not full frame dimensions in each record.

```bash
mkdir -p /work/apps

cat > /work/apps/pipeline_dashboard.py <<'EOF'
#!/usr/bin/env python3
import json
import os
import signal
import subprocess
import threading
import time
from collections import Counter, deque

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

EVENT_FILE = "/work/data/output/custom-detector.ndjson"
PIPELINE_NAME = "05-custom-detector"
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "8010"))

# Educational policy example: flag cup if it stays in a right-side misplaced zone.
MISPLACED_LABEL = "cup"
MISPLACED_HOLD_SECONDS = 1.0
ALERT_IN_ZONE = "Cup present in right-side restricted zone."
ALERT_RESOLVED = "Cup moved back out of the right-side restricted zone."
MISPLACED_ZONE = {
    "x_min": 0.65,
    "x_max": 1.0,
    "y_min": 0.0,
    "y_max": 1.0,
}

state = {
    "records_processed": 0,
    "frame_label_counts": Counter(),
    "recent": deque(maxlen=20),
    "alerts": deque(maxlen=20),
    "right_zone_has_cup": False,
    "right_zone_since": None,
    "right_zone_alerted": False,
    "status": "starting"
}

state_lock = threading.Lock()

pipeline_proc = None

app = FastAPI(title="Perception dashboard")


def normalize_label(value: str) -> str:
    label = value.strip().lower()
    if not label:
        return ""
    for sep in ("#", "(", "|"):
        if sep in label:
            label = label.split(sep, 1)[0].strip()
    parts = label.split()
    return parts[0] if parts else ""


def parse_frame_detections(record):
    perception = (record or {}).get("perception") or {}
    layers = perception.get("layers") or []

    frame_width = 0.0
    frame_height = 0.0
    for layer in layers:
        for det in (layer or {}).get("detections") or []:
            if (det or {}).get("type") != "VideoFrame":
                continue
            payload = (det or {}).get("data") or {}
            frame_width = float(payload.get("originalWidth") or 0.0)
            frame_height = float(payload.get("originalHeight") or 0.0)
            if frame_width > 0 and frame_height > 0:
                break
        if frame_width > 0 and frame_height > 0:
            break

    results = []
    for layer in layers:
        if layer.get("contentType") != "genericObject":
            continue
        for det in (layer or {}).get("detections") or []:
            if (det or {}).get("type") != "Rect":
                continue
            payload = (det or {}).get("data") or {}
            label = normalize_label(str(payload.get("text") or ""))
            if not label:
                continue

            x = float(payload.get("x") or 0.0)
            y = float(payload.get("y") or 0.0)
            w = float(payload.get("width") or 0.0)
            h = float(payload.get("height") or 0.0)

            cx = None
            cy = None
            if frame_width > 0 and frame_height > 0:
                cx = max(0.0, min(1.0, (x + 0.5 * w) / frame_width))
                cy = max(0.0, min(1.0, (y + 0.5 * h) / frame_height))
            elif 0.0 <= x <= 1.0 and 0.0 <= y <= 1.0 and 0.0 <= w <= 1.0 and 0.0 <= h <= 1.0:
                # Fallback for streams that already emit normalized coordinates.
                cx = max(0.0, min(1.0, x + 0.5 * w))
                cy = max(0.0, min(1.0, y + 0.5 * h))

            results.append({
                "label": label,
                "cx": cx,
                "cy": cy,
            })

    return results


def extract_fallback_labels(obj):
    labels = []

    def recurse(x):
        if isinstance(x, dict):
            for key, value in x.items():
                if key.lower() in ("label", "class", "class_name", "name", "text") and isinstance(value, str):
                    v = normalize_label(value)
                    if v:
                        labels.append(v)
                recurse(value)
        elif isinstance(x, list):
            for item in x:
                recurse(item)

    recurse(obj)
    return labels


def in_misplaced_zone(cx, cy):
    if cx is None or cy is None:
        return False
    return (
        MISPLACED_ZONE["x_min"] <= cx <= MISPLACED_ZONE["x_max"]
        and MISPLACED_ZONE["y_min"] <= cy <= MISPLACED_ZONE["y_max"]
    )


def append_alert_locked(now, message):
    state["alerts"].appendleft({
        "ts": int(now),
        "message": message,
    })


def follow_events(path):
    while not os.path.exists(path):
        time.sleep(0.5)

    with open(path, "r", encoding="utf-8") as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.2)
                continue
            yield line.strip()


def event_worker():
    for line in follow_events(EVENT_FILE):
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        now = time.time()
        detections = parse_frame_detections(event)

        # Fallback path: if structured Rect parsing misses a model-specific schema,
        # still extract labels so the dashboard remains useful.
        if not detections:
            detections.extend(
                {"label": label, "cx": None, "cy": None}
                for label in extract_fallback_labels(event)
            )

        with state_lock:
            frame_labels = {d["label"] for d in detections}
            cup_in_zone_this_frame = any(
                d["label"] == MISPLACED_LABEL and in_misplaced_zone(d["cx"], d["cy"])
                for d in detections
            )

            state["right_zone_has_cup"] = cup_in_zone_this_frame

            if cup_in_zone_this_frame:
                if state["right_zone_since"] is None:
                    state["right_zone_since"] = now
                elif (now - state["right_zone_since"] >= MISPLACED_HOLD_SECONDS) and not state["right_zone_alerted"]:
                    append_alert_locked(now, ALERT_IN_ZONE)
                    state["right_zone_alerted"] = True
            else:
                if state["right_zone_alerted"]:
                    append_alert_locked(now, ALERT_RESOLVED)
                state["right_zone_since"] = None
                state["right_zone_alerted"] = False

            for label in frame_labels:
                state["frame_label_counts"][label] += 1
            state["records_processed"] += 1
            if frame_labels:
                state["recent"].appendleft({"ts": int(now), "labels": sorted(frame_labels)})


def start_pipeline():
    global pipeline_proc
    pipeline_proc = subprocess.Popen(
        ["./tools/amp-menu", PIPELINE_NAME],
        cwd="/work",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT
    )
    with state_lock:
        state["status"] = "running"


def stop_pipeline():
    global pipeline_proc
    if pipeline_proc and pipeline_proc.poll() is None:
        pipeline_proc.send_signal(signal.SIGTERM)
        try:
            pipeline_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pipeline_proc.kill()
    with state_lock:
        state["status"] = "stopped"


@app.on_event("startup")
def on_startup():
    os.makedirs("/work/data/output", exist_ok=True)
    start_pipeline()
    threading.Thread(target=event_worker, daemon=True).start()


@app.on_event("shutdown")
def on_shutdown():
    stop_pipeline()


@app.get("/", response_class=HTMLResponse)
def dashboard():
    return """
<!doctype html>
<html>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width,initial-scale=1'>
  <title>Perception dashboard</title>
  <style>
    body { font-family: 'Trebuchet MS', sans-serif; margin: 24px; background: #f4f7f8; color: #152025; }
    .card { background: #fff; border-radius: 12px; padding: 16px; margin-bottom: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
    h1 { margin-top: 0; }
    li { margin: 6px 0; }
        #zone-state { color: #fff; font-weight: 700; padding: 8px 12px; border-radius: 8px; display: inline-block; }
        .content-grid { display: grid; grid-template-columns: 1.2fr 1fr; gap: 12px; align-items: start; }
        .left-col .card:last-child { margin-bottom: 0; }
        .right-col .card { margin-bottom: 0; }
        @media (max-width: 900px) {
            .content-grid { grid-template-columns: 1fr; }
        }
  </style>
</head>
<body>
  <h1>Custom detector dashboard</h1>
  <div class='card'>
        <div id='status'></div>
		<div id='zone-state'></div>
		<div id='records'></div>
  </div>
    <div class='content-grid'>
        <div class='left-col'>
            <div class='card'>
			<h3>Policy alerts</h3>
			<ul id='alerts'></ul>
		</div>
            <div class='card'>
			<h3>Frame count with object</h3>
                <ul id='counts'></ul>
            </div>
        </div>
        <div class='right-col'>
			<div class='card'>
				<h3>Recent object detections</h3>
				<ul id='recent'></ul>
			</div>
        </div>
    </div>
  <script>
        function renderList(targetId, items, toText) {
            const el = document.getElementById(targetId);
            el.innerHTML = '';
            items.forEach((item) => {
                const li = document.createElement('li');
                li.textContent = toText(item);
                el.appendChild(li);
            });
        }

    async function refresh() {
      const r = await fetch('/api/state');
      const s = await r.json();
    document.getElementById('status').textContent = 'Pipeline status: ' + s.status;
    const zoneState = document.getElementById('zone-state');
    if (s.right_zone_has_cup) {
        zoneState.style.background = '#c62828';
        zoneState.textContent = 'RED: Right-hand zone has a cup';
    } else {
        zoneState.style.background = '#2e7d32';
        zoneState.textContent = 'GREEN: Right-hand zone is empty';
    }
	document.getElementById('records').textContent = 'Frame events processed (NDJSON messages): ' + s.records_processed;
            renderList(
                'counts',
                Object.entries(s.frame_label_counts).sort((a, b) => b[1] - a[1]),
                ([k, v]) => `${k}: ${v}`
            );
            renderList(
                'recent',
                s.recent,
                (e) => `${new Date(e.ts * 1000).toLocaleTimeString()} -> ${e.labels.join(', ')}`
            );
            renderList(
                'alerts',
                s.alerts,
                (a) => `${new Date(a.ts * 1000).toLocaleTimeString()} -> ${a.message}`
            );
    }
    setInterval(refresh, 1000);
    refresh();
  </script>
</body>
</html>
"""


@app.get("/api/state")
def api_state():
    with state_lock:
        return {
            "status": state["status"],
            "records_processed": state["records_processed"],
            "right_zone_has_cup": state["right_zone_has_cup"],
            "frame_label_counts": dict(state["frame_label_counts"]),
            "recent": list(state["recent"]),
            "alerts": list(state["alerts"])
        }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=DASHBOARD_PORT)

EOF
```

## Understand what this app is doing

The code block includes several practical pieces. This section explains the parts you should care about most when connecting a Python app to a Perception Kit pipeline.

### Pipeline-coupled parts (most important)

1. `start_pipeline()` launches `./tools/amp-menu 05-custom-detector` from `/work`.
This is the key integration point. Your app does not run inference itself. It starts the existing pipeline entry, which in turn runs the GStreamer pipeline and model inference.

2. The pipeline writes events through `ampcomm` to `/work/data/output/custom-detector.ndjson`.
Because the pipeline is configured with `ampcomm method=file ...`, detections become structured JSON lines. This file is the contract between your inference pipeline and your Python logic.

3. `follow_events()` tails the NDJSON file continuously.
This gives you near real-time consumption of inference results without direct coupling to GStreamer internals. As long as the pipeline keeps writing events, your app keeps receiving them.

4. `event_worker()` converts raw records into application state and policy signals.
It parses each JSON line, extracts `genericObject` rectangle detections (with a fallback label scan when needed), updates frame-based counts for labels seen in each record, and evaluates a misplaced-item zone rule with hold-time and resolve behavior. This is where you could replace with your own logic, specific to your use-case.

5. `stop_pipeline()` shuts the pipeline down with the app.
When the app exits, it sends `SIGTERM` to the pipeline process. This avoids leaving background pipeline processes running accidentally.

### Standard app parts (important but swappable)

1. FastAPI startup/shutdown hooks are a standard Python web pattern.
They are used here to start and stop background work cleanly. You can replace this with another framework or a plain Python service loop.

2. The `/api/state` endpoint is a standard JSON API.
Any frontend, CLI, or monitoring tool can read this data. You can replace the HTML page with another client and keep this endpoint unchanged.

3. The HTML and JavaScript dashboard is a standard polling UI.
It refreshes every second and renders frame count with object, recent object detections, right-zone status, and policy alerts. This is only a display layer. You can swap it for React, Vue, Streamlit, Grafana, or no UI at all.

## Run the application

Run the app as you would normally run a python script:

```bash
python3 /work/apps/pipeline_dashboard.py
```

Then open `http://localhost:8010` in your browser to view your basic app.

When the cup is on the right-hand side (misplaced zone), the dashboard status should turn red and show the active policy condition.

![Dashboard showing red status when the cup is detected in the right-side restricted zone#center](Red.png "Red status with cup in the right-side restricted zone")

After you move the cup to the left side (expected zone) or remove it from the frame, the dashboard should turn green and the policy condition should clear.

![Dashboard showing green status after the cup is moved to the left-side expected zone#center](Green.png "Green status after the cup returns to the expected zone")

{{% notice Note %}}
To produce the WebRTC images, the pipeline was adapted to include `ampsink` and `amposd`, as discussed above, so that the WebRTC viewer is also available.
{{% /notice %}}

## What you've learned and what's next

You now have a practical pattern to consume Perception Kit inference events in a local web app and apply policy logic beyond raw detection. Next, you can adapt the same event-processing path to restricted-zone monitoring, occupancy thresholds, or queue-based downstream integration.

The Arm Perception Pipeline Kit is in an early release, with active plans for further development. We are keen to see what the community can build atop the kit, and would welcome any feedback or feature requests.

Please consider providing any feedback at the [Arm Perception Pipeline Kit Feedback Form](placeholder-link)

