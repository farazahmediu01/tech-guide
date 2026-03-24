# Lesson 2: Function Tools & Context Objects

> **Chapter:** 34 — OpenAI Agents SDK
> **Date:** 2026-02-26
> **Status:** In Progress
> **Project file:** `openai-agents-sdk/support_desk.py`

---

## The Big Idea

An agent without tools is just a chatbot. Tools give agents **hands** — the ability
to take actions in the real world. Context objects give those hands **memory** — shared
state that persists across every tool call in a run.

| Without Tools | With Tools |
|---------------|------------|
| "I don't have access to orders" | Queries database, returns real status |
| "Please call our hotline" | Creates ticket, returns ticket number |
| "I've noted your request" | Sends email, confirms delivery |
| "I think the answer is..." | Retrieves exact documentation |

---

## Concept 1 — The `@function_tool` Decorator

Transforms any Python function into an agent-callable tool.

```python
from agents import Agent, Runner, function_tool

@function_tool
def get_current_time() -> str:
    """Return the current time in HH:MM:SS format."""
    from datetime import datetime
    return datetime.now().strftime("%H:%M:%S")

agent = Agent(
    name="TimeAgent",
    instructions="Help users with time-related questions.",
    tools=[get_current_time],
)

result = Runner.run_sync(agent, "What time is it?")
print(result.final_output)
# The current time is 14:32:17.
```

### What happens under the hood

The `@function_tool` decorator:
1. Inspects your function signature
2. Generates a JSON schema the LLM can understand
3. Extracts the description from your docstring
4. Handles calling your function when the agent decides to use it

### Type hints + docstrings = the tool's API contract

```python
@function_tool
def add_task(title: str, priority: int = 1) -> str:
    """
    Add a new task to the task list.

    Args:
        title: The task description (required)
        priority: Priority level 1-5 where 5 is highest (optional, default 1)
    Returns:
        Confirmation message with task ID
    """
    task_id = "task_" + str(hash(title))[:8]
    return f"Created task {task_id}: '{title}' with priority {priority}"
```

Generates this schema (what the LLM actually reads):

```json
{
  "name": "add_task",
  "description": "Add a new task to the task list.",
  "parameters": {
    "properties": {
      "title":    { "type": "string",  "description": "The task description (required)" },
      "priority": { "type": "integer", "description": "Priority level 1-5...", "default": 1 }
    },
    "required": ["title"]
  }
}
```

### Three rules for good tools

| Rule | Why |
|------|-----|
| **Type hints are required** | Defines schema types and `required` fields |
| **Docstring is the API contract** | The LLM reads this to decide *when* and *how* to call the tool |
| **Optional params get defaults** | `priority: int = 1` → excluded from `required` array |

> **Production tip:** Write docstrings as if explaining the tool to a colleague.
> Vague docstrings produce unpredictable tool usage.

---

## Concept 2 — Context Objects

Tools are **stateless by default** — each call is independent with no shared memory.
Context objects fix that.

A context object is a **Pydantic `BaseModel` holding shared state**, injected into
every tool, handoff, and agent in a single run.

```python
from pydantic import BaseModel

class TaskManagerContext(BaseModel):
    user_id: str | None = None
    current_project: str | None = None
    tasks_added: int = 0
    tasks: list[dict] = []
```

### Wiring context to your agent

Use the generic type `Agent[YourContext]` and pass context to `Runner.run_sync()`:

```python
from agents import Agent, Runner

agent = Agent[TaskManagerContext](
    name="TaskManager",
    instructions="Help users manage tasks.",
    tools=[],
)

context = TaskManagerContext(user_id="user_123", current_project="Project Alpha")

result = Runner.run_sync(agent, "What's my current project?", context=context)
# Output: Your current project is Project Alpha.
```

> **Key rule:** Context is **not sent to the LLM**. It's purely local state your
> code can read and write. The agent accesses it only through tool return values
> or dynamic instructions.

---

## Concept 3 — `RunContextWrapper` in Tools

To access context inside a tool, add `RunContextWrapper[YourContext]` as the
**first parameter**. The SDK injects it automatically — users never provide it.

```python
from agents import function_tool, RunContextWrapper

@function_tool
def add_task(
    ctx: RunContextWrapper[TaskManagerContext],  # injected by SDK — NOT in schema
    title: str,
    priority: int = 1
) -> str:
    """
    Add a new task to the task list.

    Args:
        title: The task description
        priority: Priority level 1-5 where 5 is highest
    Returns:
        Confirmation message with task ID
    """
    ctx.context.tasks_added += 1                          # mutate — persists across calls
    task_id = f"task_{len(ctx.context.tasks) + 1:03d}"
    ctx.context.tasks.append({
        "id": task_id,
        "title": title,
        "priority": priority,
        "status": "pending",
        "project": ctx.context.current_project,
    })
    return f"Created {task_id}: '{title}' (P{priority})"
```

### `RunContextWrapper` properties

| Property | Contents |
|----------|----------|
| `ctx.context` | Your Pydantic model instance (read/write) |
| `ctx.usage` | Token usage — `requests`, `input_tokens`, `output_tokens`, `total_tokens` |

> **Critical:** `RunContextWrapper` must always be the **first** parameter.
> The SDK detects it by position and excludes it from the JSON schema.
> If the LLM tried to fill it in, it would send arbitrary data into your
> state object — a serious security and correctness bug.

---

## Complete Working Example — TaskManager Agent

```python
from agents import Agent, Runner, function_tool, RunContextWrapper
from pydantic import BaseModel

# --- Context Model ---
class TaskManagerContext(BaseModel):
    user_id: str | None = None
    current_project: str | None = None
    tasks_added: int = 0
    tasks: list[dict] = []

# --- Tools ---
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
        Confirmation message with task ID
    """
    task_id = f"task_{len(ctx.context.tasks) + 1:03d}"
    ctx.context.tasks.append({
        "id": task_id,
        "title": title,
        "priority": priority,
        "status": "pending",
        "project": ctx.context.current_project,
    })
    ctx.context.tasks_added += 1
    return f"Created {task_id}: '{title}' (P{priority})"


@function_tool
def list_tasks(ctx: RunContextWrapper[TaskManagerContext]) -> str:
    """List all tasks for the current project."""
    tasks = [t for t in ctx.context.tasks if t["project"] == ctx.context.current_project]
    if not tasks:
        return f"No tasks found for '{ctx.context.current_project}'"
    lines = [f"Tasks for '{ctx.context.current_project}':"]
    for t in tasks:
        icon = "[x]" if t["status"] == "complete" else "[ ]"
        lines.append(f"  {icon} {t['id']}: {t['title']} (P{t['priority']})")
    return "\n".join(lines)


@function_tool
def complete_task(ctx: RunContextWrapper[TaskManagerContext], task_id: str) -> str:
    """
    Mark a task as complete.

    Args:
        task_id: The ID of the task to complete (e.g. 'task_001')
    Returns:
        Confirmation message
    """
    for task in ctx.context.tasks:
        if task["id"] == task_id:
            task["status"] = "complete"
            return f"Completed {task_id}: '{task['title']}'"
    return f"Task {task_id} not found"


# --- Agent ---
task_manager = Agent[TaskManagerContext](
    name="TaskManager",
    instructions="""You are a task management assistant. Help users:
    - Add new tasks with priorities (1=low, 5=critical)
    - List their current tasks
    - Mark tasks as complete
    Always confirm actions and provide helpful summaries.""",
    tools=[add_task, list_tasks, complete_task],
)

# --- Run ---
context = TaskManagerContext(user_id="dev_42", current_project="Digital FTE MVP")

result = Runner.run_sync(
    task_manager,
    "Add: 'Design agent architecture' (P4), 'Write function tools' (P3). Then show the list.",
    context=context,
)
print(result.final_output)

# Mark one complete
result = Runner.run_sync(task_manager, "I finished the architecture design. Mark it done.", context=context)
print(result.final_output)
```

Expected output:

```
Tasks for 'Digital FTE MVP':
  [ ] task_001: Design agent architecture (P4)
  [ ] task_002: Write function tools (P3)

Completed task_001: 'Design agent architecture'
Tasks for 'Digital FTE MVP':
  [x] task_001: Design agent architecture (P4)
  [ ] task_002: Write function tools (P3)
```

---

## Progressive Project — Support Desk Assistant

Extend `support_desk.py` from Lesson 1 with real tools.

### Step 1 — Context model

```python
from pydantic import BaseModel

class SupportContext(BaseModel):
    customer_id: str
    customer_name: str
    account_tier: str = "standard"
    tickets: list[dict] = []
```

### Step 2 — Fake orders database

```python
ORDERS_DB = {
    "ORD-001": {"product": "Laptop Pro",     "status": "delivered",  "date": "2026-02-10"},
    "ORD-002": {"product": "Wireless Mouse", "status": "in transit", "date": "2026-02-23"},
    "ORD-003": {"product": "USB-C Hub",      "status": "processing", "date": "2026-02-25"},
}
```

### Step 3 — Three tools to build

```python
@function_tool
def lookup_order(order_id: str) -> str:
    """
    Look up an order by ID.

    Args:
        order_id: The order ID (e.g. 'ORD-001')
    Returns:
        Order details including product, status, and date
    """
    order = ORDERS_DB.get(order_id)
    if not order:
        return f"Order {order_id} not found."
    return f"Order {order_id}: {order['product']} — {order['status']} (ordered {order['date']})"


@function_tool
def create_ticket(
    ctx: RunContextWrapper[SupportContext],
    subject: str,
    description: str,
    priority: str = "medium",
) -> str:
    """
    Create a support ticket for the current customer.

    Args:
        subject: Brief description of the issue
        description: Detailed description
        priority: low | medium | high | critical
    Returns:
        Ticket ID and confirmation
    """
    ticket_id = f"TKT-{len(ctx.context.tickets) + 1:04d}"
    ctx.context.tickets.append({
        "id": ticket_id,
        "subject": subject,
        "description": description,
        "priority": priority,
        "customer": ctx.context.customer_name,
    })
    return f"Ticket {ticket_id} created: '{subject}' ({priority} priority)"


@function_tool
def check_account_status(ctx: RunContextWrapper[SupportContext]) -> str:
    """Return current customer account information."""
    return (
        f"Customer: {ctx.context.customer_name} ({ctx.context.customer_id})\n"
        f"Tier: {ctx.context.account_tier}\n"
        f"Open tickets: {len(ctx.context.tickets)}"
    )
```

### Step 4 — Wire it up

```python
support_agent = Agent[SupportContext](
    name="SupportDesk",
    instructions="""You are TechCorp customer support.
    Use your tools to:
    - Look up order status with lookup_order
    - Create support tickets with create_ticket
    - Check account information with check_account_status
    Always confirm actions taken and ask if there's anything else you can help with.""",
    tools=[lookup_order, create_ticket, check_account_status],
)

context = SupportContext(
    customer_id="CUST-42",
    customer_name="Alex Chen",
    account_tier="premium",
)

result = Runner.run_sync(
    support_agent,
    "Check my order ORD-001 and if it's delayed create a ticket for me.",
    context=context,
)
print(result.final_output)
```

Run with:

```bash
uv run python support_desk.py
```

### Success criteria

- `lookup_order` returns real data from `ORDERS_DB`
- `create_ticket` appends to `context.tickets` and returns a ticket ID
- `check_account_status` reads `customer_name` and `account_tier` from context
- Agent uses all three tools correctly in one conversation

---

## Key Takeaways

| Concept | One-liner |
|---------|-----------|
| `@function_tool` | Decorator that turns a Python function into an LLM-callable tool |
| Type hints | Define the JSON schema — required fields, types, and defaults |
| Docstring | The tool's description — what the LLM reads to decide when to call it |
| `BaseModel` context | Pydantic model holding shared state for a run |
| `Agent[TContext]` | Generic annotation that type-checks context throughout your system |
| `RunContextWrapper` | Injected first param giving tools access to `ctx.context` and `ctx.usage` |
| Context mutation | Tools can write to `ctx.context` — changes persist across tool calls |

---

## What's Next

Lesson 3 — **Agents as Tools & Multi-Agent Orchestration**

Your Support Desk currently does everything itself. In Lesson 3 you'll add
specialist sub-agents — a researcher and a writer — that the main agent
can delegate to using `agent.as_tool()`.
