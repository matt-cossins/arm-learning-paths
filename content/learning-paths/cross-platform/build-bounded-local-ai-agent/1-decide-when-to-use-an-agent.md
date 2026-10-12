---
title: Decide when to use an agent
description: Compare deterministic software, direct model calls, tool-calling assistants, and bounded agents.
weight: 2

### FIXED, DO NOT MODIFY
layout: learningpathall
---

The inference service from the first Learning Path accepts a task and returns a model result. It does not decide whether a request needs a model, a Python function, or a tool. That decision belongs to the application.

## Compare four application designs

| Design | Who chooses the next operation? | State across operations | Suitable use |
| --- | --- | --- | --- |
| Deterministic software | Application code | Defined by the program | Exact rules, calculations, validation, and known workflows |
| Direct model call | Application code makes one model request | Prompt and response | Explanation, rewriting, and other language-only tasks |
| Tool-calling assistant | Model proposes a tool; application executes once | One request and tool result | A language interface for a known operation |
| Bounded agent | Model can choose another action after each observation | Goal, observations, limits, and trace | Tasks where the next step depends on an earlier result |

A chatbot is not automatically an agent. A model becomes part of an agent when application code lets it select an action, observes the result, and decide whether another action is needed.

## Keep authority in application code

The model can propose:

- A final answer
- A registered tool name
- Arguments for that tool

The application still decides:

- Which tools exist
- Which argument schema each tool accepts
- Whether an action is allowed
- How long a tool may run
- How many steps and tool calls are available
- Whether a mutating action needs confirmation
- When repeated or invalid actions stop the loop

This separation matters because model output is untrusted input. A tool request is a proposal, not permission to execute arbitrary Python or shell commands.

## Use the least flexible route

Choose the simplest route that can complete the request:

1. Use deterministic software when the request can be recognized and handled exactly.
2. Use a direct model call when the task needs language generation but no external action.
3. Use the agent loop only when a result can change the next action.

This order reduces model calls, makes exact tasks predictable, and keeps tool access limited to requests that need it.

## What you've learned

An agent is an application control loop, not a property of the model server. Next, you will place that loop above the reusable inference service built in Path 1.
