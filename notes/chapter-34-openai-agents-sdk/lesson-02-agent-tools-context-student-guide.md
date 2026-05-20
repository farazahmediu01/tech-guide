---
marp: true
theme: default
class: invert
style: |
  section {
    font-size: 22px;
  }
  section.small {
    font-size: 18px;
  }
  section h2 {
    font-size: 1.4em;
  }
  section h3 {
    font-size: 1.1em;
  }
  pre {
    font-size: 0.85em;
  }
---

# OpenAI Agents SDK
## Lesson 2 — Agent, Tools & Context

**The three primitives that make every agent work**

Source: `openai-agents-sdk/00_task_management_agent.py`
Progression: Terminal → Chainlit → FastAPI → React

---

## What You Will Learn

By the end of this lesson you will be able to:

- Explain what an Agent, Tool, and Context are — in plain English
- Read and understand the `00_task_management_agent.py` file completely
- Use `@function_tool` to give an agent real capabilities
- Use `RunContextWrapper` to share state between tools
- Run an agent with `Runner.run_sync` and inspect its output
- Explain why this agent is different from the chatbot you already built

---

## The Big Picture — What Is an Agent?

A **chatbot** answers questions using only its training.

An **agent** can take actions using tools — and remember things across a conversation.

```
Chatbot:   User → Model → Response
                   ↑
               (training only)

Agent:     User → Model → Decides which Tool to call
                   ↑              ↓
               (training)     Tool runs → Result → Model → Response
                                              ↑
                                         (context — shared memory)
```

The model is the brain. Tools are the hands. Context is the memory.

---

## The Dataset / Code We Use

We are teaching with one file:

```
openai-agents-sdk/00_task_management_agent.py
```

It builds a **Task Manager Agent** that can:
- Add tasks to a list
- Show the current task list
- Mark a task as complete

**Why this file?** One file. Three concepts. Zero hidden complexity.
Students run it, see output, understand everything.

---

## Tool Setup

```bash
# Install the SDK
uv add openai-agents pydantic python-dotenv

# Set your API key in .env
OPENAI_API_KEY=your_key_here
```

```python
# Import the three things you need every time
from agents import Agent, Runner, function_tool, RunContextWrapper
from pydantic import BaseModel
```

> You will use these four imports in every agent you build.
> Memorize them like you memorized `from flask import Flask`.

---

## Concept 1 — Context (The Job Folder)

### What question does it answer?
*"How do tools share data with each other during a conversation?"*

### How it works
Context is a Pydantic model. It is created once before the agent runs.
Every tool receives it automatically via `RunContextWrapper`.
Think of it as a **job folder** — everything about this session lives inside it.

```python
class TaskManagerContext(BaseModel):
    user_id: str
    current_project: str
    tasks_added: int = 0
    tasks: list[dict] = []
```

> The context is NOT sent to the LLM. It is private state that only your tools can read and write.

---

## Concept 1 — Context (continued)

### How it is created and passed

```python
# You create it before running the agent
context = TaskManagerContext(
    user_id="dev_42",
    current_project="Digital FTE MVP"
)

# You pass it into Runner
result = Runner.run_sync(
    task_manager,
    "Add 'Design architecture' with priority 4",
    context=context          # ← here
)

# After the run, you can inspect it directly
print(context.tasks_added)  # ← the context object still exists
print(context.tasks)
```

---

## Try It Yourself — Concept 1

1. Add a new field `owner: str = "unknown"` to `TaskManagerContext`
2. Set it to your name when creating the context object
3. Print it after the run — does it still hold your name?

**Think about it:** Why is context a Pydantic `BaseModel` and not a plain Python dictionary?

**Challenge:** What would happen if two users ran the agent at the same time with the same context object? Is that safe?

---

## Concept 2 — Tool (The Agent's Hands)

### What question does it answer?
*"How does the agent actually DO something — not just talk about it?"*

### How it works
A tool is a Python function decorated with `@function_tool`.
The agent reads the function's **docstring** to understand when to call it.
The function's **type hints** tell the agent what arguments to pass.

```python
@function_tool
def add_task(
    ctx: RunContextWrapper[TaskManagerContext],  # ← always first
    title: str,                                  # ← agent fills this
    priority: int = 1                            # ← agent fills this
) -> str:
    """
    Add a new task to the task list.
    Args:
        title: The task description
        priority: Priority level 1-5 where 5 is highest
    Returns:
        Confirmation with task ID
    """
```

> The docstring is the tool's contract with the LLM. Write it clearly or the agent will misuse the tool.

---

<!-- _class: invert small -->

## Concept 2 — Tool (full implementation)

```python
@function_tool
def add_task(
    ctx: RunContextWrapper[TaskManagerContext],
    title: str,
    priority: int = 1
) -> str:
    """
    Add a new task to the task list.
    Args:
        title: The task description
        priority: Priority level 1-5 where 5 is highest
    Returns:
        Confirmation with task ID
    """
    task_id = f"task_{len(ctx.context.tasks) + 1:03d}"  # task_001, task_002...
    ctx.context.tasks.append({
        "id": task_id,
        "title": title,
        "priority": priority,
        "status": "pending",
        "project": ctx.context.current_project,
    })
    ctx.context.tasks_added += 1
    return f"Created {task_id}: '{title}' (P{priority})"
```

`ctx.context` is how you read and write the shared job folder from inside a tool.

---

## Try It Yourself — Concept 2

1. Add a new tool `cancel_task` that sets a task's status to `"cancelled"` by task ID
2. Write a clear docstring so the agent knows when to use it
3. Add it to the agent's `tools` list
4. Ask the agent: *"Cancel task_001"* — does it work?

**Think about it:** The agent decides WHICH tool to call. You don't call tools yourself. What tells the agent to pick `add_task` vs `list_tasks`?

**Challenge:** What happens if you remove the docstring from a tool? Try it.

---

## Concept 3 — Agent (The Brain)

### What question does it answer?
*"What holds everything together — the tools, the instructions, the model?"*

### How it works
`Agent` is the configuration object. It does not run by itself.
It holds: the name, the system instructions, the list of tools, and the model.
The type parameter `Agent[TaskManagerContext]` tells it what context shape to expect.

```python
task_manager = Agent[TaskManagerContext](
    name="TaskManager",
    instructions="""You are a task management assistant.
    Help users add, list, and complete tasks.
    Always confirm actions and show the updated list.""",
    tools=[add_task, list_tasks, complete_task],
)
```

> `instructions` is the system prompt. This is where you define the agent's personality and rules.

---

## Concept 3 — Runner (The Engine)

`Agent` is the config. `Runner` is what actually executes it.

```python
# Run the agent once
result = Runner.run_sync(
    task_manager,                            # which agent
    "Add 'Design architecture' (P4).",       # user message
    context=context                          # shared memory
)

print(result.final_output)   # the agent's final text response
```

```python
# Run it again — same context object, state persists
result = Runner.run_sync(
    task_manager,
    "I finished the architecture. Mark task_001 done.",
    context=context           # ← same context = tasks still exist
)

print(f"Tasks added this session: {context.tasks_added}")
```

> `run_sync` is the blocking version. Later you will use `run` (async) inside FastAPI.

---

## Try It Yourself — Concept 3

1. Change `instructions` to make the agent more strict:
   *"Never add a task without a priority. If priority is missing, ask for it."*
2. Test it by saying: *"Add task: Write the README"* (no priority)
3. Does the agent ask for the priority before adding?

**Think about it:** If you create a new `context` object for the second `Runner.run_sync` call, what happens to the tasks from the first run?

**Challenge:** What is `result.final_output`? What else is on the `result` object? Try `print(dir(result))`.

---

## The Full File — All Three Concepts Together

<!-- _class: invert small -->

```python
from agents import Agent, Runner, function_tool, RunContextWrapper
from pydantic import BaseModel

class TaskManagerContext(BaseModel):          # Concept 1 — Context
    user_id: str
    current_project: str
    tasks_added: int = 0
    tasks: list[dict] = []

@function_tool
def add_task(ctx: RunContextWrapper[TaskManagerContext], title: str, priority: int = 1) -> str:
    """Add a new task to the task list."""   # Concept 2 — Tool
    task_id = f"task_{len(ctx.context.tasks) + 1:03d}"
    ctx.context.tasks.append({"id": task_id, "title": title, "priority": priority, "status": "pending"})
    ctx.context.tasks_added += 1
    return f"Created {task_id}: '{title}' (P{priority})"

@function_tool
def list_tasks(ctx: RunContextWrapper[TaskManagerContext]) -> str:
    """List all tasks for the current project."""
    tasks = [t for t in ctx.context.tasks if t["project"] == ctx.context.current_project]
    if not tasks:
        return f"No tasks for '{ctx.context.current_project}'"
    lines = [f"Tasks for '{ctx.context.current_project}':"]
    for t in tasks:
        icon = "[x]" if t["status"] == "complete" else "[ ]"
        lines.append(f"  {icon} {t['id']}: {t['title']} (P{t['priority']})")
    return "\n".join(lines)

task_manager = Agent[TaskManagerContext](     # Concept 3 — Agent
    name="TaskManager",
    instructions="You are a task management assistant. Help users add, list, and complete tasks.",
    tools=[add_task, list_tasks],
)

context = TaskManagerContext(user_id="dev_42", current_project="Digital FTE MVP")
result = Runner.run_sync(task_manager, "Add 'Design architecture' (P4). Then list tasks.", context=context)
print(result.final_output)
```

---

## What Makes This Agent Different From Your Chatbot?

| | Chatbot (ChatCompletions) | Agent (OpenAI Agents SDK) |
|--|--------------------------|--------------------------|
| Can take actions | No | Yes — via tools |
| Remembers tasks | No | Yes — via context |
| Calls Python functions | No | Yes — automatically |
| Has persistent state | No | Yes — context survives across runs |
| Decides what to do | No | Yes — picks which tool to call |

**The context object is the key difference.**
After two `Runner.run_sync` calls, `context.tasks` still has everything.
A chatbot has no equivalent. Every call starts from zero.

---

## Common Mistakes

| Mistake | Wrong | Correct |
|---------|-------|---------|
| Forgetting `ctx` as first arg | `def add_task(title, priority)` | `def add_task(ctx: RunContextWrapper[...], title, priority)` |
| Writing a bad docstring | `"""adds task"""` | Describe args, what it does, what it returns |
| Creating new context per run | `Runner.run_sync(..., context=TaskManagerContext(...))` | Create context once, reuse it |
| Calling tools yourself | `add_task(ctx, "my task")` | Let the agent decide — just run `Runner.run_sync` |
| Using `ctx` instead of `ctx.context` | `ctx.tasks.append(...)` | `ctx.context.tasks.append(...)` |

---

## Upgrading the Agent — What Changes in `00_practice.py`

The refactor teaches one lesson: **model your data properly.**

```python
# Before (00_task_management_agent.py) — tasks as plain dicts
tasks: list[dict] = []
ctx.context.tasks.append({"id": task_id, "title": title, ...})

# After (00_practice.py) — tasks as Pydantic models
class Task(BaseModel):
    id: int
    title: str
    status: TaskStatus = TaskStatus.PENDING
    priority: int = Field(default=5, ge=1, le=5)

tasks: list[Task] = Field(default_factory=list)
ctx.context.tasks.append(Task(id=..., title=title, priority=priority))
```

Why? Because `Task` as a Pydantic model gives you:
- Validation (priority must be 1–5, enforced)
- IDE autocomplete on every field
- Serialization to JSON for free

---

## Putting It All Together — The Build Progression

Every stage produces something students can see and touch:

```
Stage 1 — Terminal (today)
  Run 00_task_management_agent.py → output in console
  Students see: the agent adding and listing tasks

Stage 2 — Chainlit (next session)
  Same agent + 25 lines of Chainlit code
  Students see: a real chat UI, agent responds in browser

Stage 3 — FastAPI (after Chainlit)
  Agent wrapped in POST /chat endpoint
  Students see: API calls in Postman, foundation for frontend

Stage 4 — React (capstone)
  React frontend calls FastAPI → agent responds in chat UI
  Students see: full-stack AI app — portfolio ready
```

Each stage adds ONE new layer. The agent code never changes.

---

## Tiered Practice Set

**Level 1 — Basic**
1. Run `00_task_management_agent.py` without changes. Read the output.
2. Print `context.tasks` after the run. What does it contain?
3. Print `context.tasks_added`. What number do you expect?

**Level 2 — Filtering**
4. Add a field `owner: str` to `TaskManagerContext`. Set it when creating context.
5. Filter `list_tasks` to only show tasks with `status == "pending"`.

**Level 3 — New Tool**
6. Add a `cancel_task` tool that sets status to `"cancelled"`.
7. Add a `get_task_by_id` tool that returns one task's details.

**Level 4 — Challenge**
8. Make the agent refuse to add duplicate task titles. Where should this check live — in the tool or in the instructions?
9. Refactor `list[dict]` to a proper `Task` Pydantic model (reproduce `00_practice.py` on your own without looking).

---

## Quick Reference Card

```python
# Imports
from agents import Agent, Runner, function_tool, RunContextWrapper
from pydantic import BaseModel

# Context — shared job folder
class MyContext(BaseModel):
    field: str = "default"

# Tool — agent's hands
@function_tool
def my_tool(ctx: RunContextWrapper[MyContext], arg: str) -> str:
    """Docstring tells the agent when and how to use this tool."""
    ctx.context.field = arg          # write to context
    return "done"                    # always return a string

# Agent — the brain
agent = Agent[MyContext](
    name="MyAgent",
    instructions="System prompt here.",
    tools=[my_tool],
)

# Runner — the engine
context = MyContext()
result = Runner.run_sync(agent, "user message", context=context)
print(result.final_output)
```

---

## What's Next

**Next session:** Wrap this agent in Chainlit.
The agent code stays exactly the same. You only add the UI layer.

```python
# Preview — this is all Chainlit needs
import chainlit as cl

@cl.on_message
async def main(message: cl.Message):
    result = Runner.run_sync(task_manager, message.content, context=context)
    await cl.Message(content=result.final_output).send()
```

**Think about it before next class:**
The context object is created once at the top of the file.
If two students use the Chainlit app at the same time — do they share the same context?
What problem does that cause, and how would you fix it?
