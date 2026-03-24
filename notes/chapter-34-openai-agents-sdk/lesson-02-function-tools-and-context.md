# Lesson 2: Function Tools & Context Objects

> **Chapter:** 34 — OpenAI Agents SDK
> **Last Updated:** 2026-03-04
> **Project file:** `openai-agents-sdk/support_desk.py`
> **Skill:** `~/.claude/skills/openai-agents-sdk/`

---

## Table of Contents

1. [The Big Picture](#the-big-picture)
2. [Function Tools — Giving Agents Hands](#function-tools--giving-agents-hands)
3. [Why Are Tools Stateless?](#why-are-tools-stateless)
4. [What Goes Wrong Without Context](#what-goes-wrong-without-context)
5. [Context Objects — The Backpack](#context-objects--the-backpack)
6. [RunContextWrapper — The Handle on the Backpack](#runcontextwrapper--the-handle-on-the-backpack)
7. [Who Creates Context? Can It Start Empty?](#who-creates-context-can-it-start-empty)
8. [Agent[TContext] Generics — The Contract](#agenttcontext-generics--the-contract)
9. [How It All Connects — The Office Analogy](#how-it-all-connects--the-office-analogy)
10. [Complete Working Example — TaskManager](#complete-working-example--taskmanager)
11. [Progressive Project — Support Desk Assistant](#progressive-project--support-desk-assistant)
12. [Try It Yourself — Exercises](#try-it-yourself--exercises)
13. [Key Takeaways](#key-takeaways)

---

## The Big Picture

> **One sentence:** Tools give agents hands — context gives those hands memory.

An agent without tools is just a chatbot. It can only respond with text.
It cannot check an order, create a ticket, send an email, or query a database.
Tools fix that. But tools alone are stateless — they forget everything between calls.
Context objects fix that.

| Without Tools | With Tools |
|---------------|------------|
| "I don't have access to orders" | Queries database, returns real status |
| "Please call our hotline" | Creates ticket, returns ticket number |
| "I've noted your request" | Sends email, confirms delivery |
| "I think the answer is..." | Retrieves exact documentation |

By the end of this lesson you will have built a **Support Desk Agent** that can
look up orders, create support tickets, and check account status — all sharing
state through a typed context object.

---

## Function Tools — Giving Agents Hands

### The `@function_tool` Decorator

The decorator transforms any Python function into an agent-callable tool.

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
# Output: The current time is 14:32:17.
```

### What the Decorator Actually Does

The `@function_tool` decorator does four things automatically:

1. Inspects your function signature
2. Generates a **JSON schema** the LLM can read
3. Extracts the description from your **docstring**
4. Handles calling your function when the agent decides to use it

> **Critical insight:** The agent never reads your Python code.
> It reads the JSON schema generated from your type hints and docstring.
> These are not optional decorations — they are the API contract.

### Type Hints + Docstrings = The API Contract

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

The SDK converts this into the schema the LLM reads:

```json
{
  "name": "add_task",
  "description": "Add a new task to the task list.",
  "parameters": {
    "properties": {
      "title": {
        "type": "string",
        "description": "The task description (required)"
      },
      "priority": {
        "type": "integer",
        "description": "Priority level 1-5 where 5 is highest (optional, default 1)",
        "default": 1
      }
    },
    "required": ["title"]
  }
}
```

The LLM reads this and knows:
- What the tool does (from `description`)
- What parameters it needs (from `properties`)
- Which are required vs optional (from `required` array)
- What types to send (from `type` fields)

### Three Rules for Good Tools

| Rule | Why It Matters |
|------|----------------|
| **Always add type hints** | Defines schema types and which fields are `required` |
| **Always write a docstring** | The LLM reads this to decide *when* and *how* to call the tool |
| **Use defaults for optional params** | `priority: int = 1` → excluded from `required` array automatically |

> **Production tip:** Write docstrings as if explaining the tool to a colleague who
> has never seen your code. Vague docstrings produce unpredictable tool usage.

---

## Why Are Tools Stateless?

### Student Question: *"Why don't tools just remember things themselves?"*

A tool is a Python function. Functions are **stateless by design** — they receive
inputs, do work, return output, and forget everything when they return.

```python
@function_tool
def add_item(name: str) -> str:
    """Add an item to the cart."""
    # When this function ends, ALL local variables are destroyed.
    # Next call starts completely fresh with zero memory.
    return f"Added {name}"
```

When `add_item("milk")` finishes, Python throws away everything inside it.
The next call to `add_item("eggs")` has zero memory of the milk call.

**This is actually a feature, not a limitation:**

| Benefit | Why |
|---------|-----|
| **Predictable** | Same input always gives same output |
| **Safe** | No hidden state that can silently corrupt |
| **Scalable** | You can run 1000 of them in parallel safely |
| **Testable** | Easy to unit test — just call the function with inputs |

The *problem* is when you need state to persist **across multiple tool calls
within one run**. That is exactly what context objects solve.

---

## What Goes Wrong Without Context

### Student Question: *"What if I just use a global variable or give tools direct database access?"*

This is the most important question before learning context objects.
Let's see both failure modes.

### Failure Mode 1 — Global Variables

```python
from agents import Agent, Runner, function_tool

# Global variable — shared across ALL users and ALL runs
cart = []

@function_tool
def add_to_cart(item: str) -> str:
    """Add an item to the shopping cart."""
    cart.append(item)
    return f"Added {item}. Cart: {cart}"

agent = Agent(name="ShopBot", instructions="Help users shop.", tools=[add_to_cart])
```

Run this with two simultaneous users:

```
User A: "Add apples"   → cart = ["apples"]
User B: "Add bananas"  → cart = ["apples", "bananas"]  ← User B sees User A's apples!
User A: "Show my cart" → cart = ["apples", "bananas"]  ← User A sees User B's bananas!
```

Global state is shared between all users. This is a **data leak and a bug**.

### Failure Mode 2 — Direct Database Access in Every Tool

```python
import sqlite3

@function_tool
def add_item(user_id: str, name: str) -> str:
    """Add an item to the cart."""
    conn = sqlite3.connect("shop.db")   # new connection on EVERY tool call
    cursor = conn.cursor()
    cursor.execute("INSERT INTO cart VALUES (?, ?)", (user_id, name))
    conn.commit()
    conn.close()
    return f"Added {name}"
```

Problems:

| Problem | What Happens |
|---------|-------------|
| **New DB connection per tool call** | 10 tool calls = 10 connections = slow and wasteful |
| **No transaction boundary** | Run fails halfway → partial data permanently in DB |
| **Tool is tightly coupled to DB schema** | Hard to test, hard to change schema later |
| **Concurrent runs corrupt data** | Two users writing simultaneously with no isolation |
| **No in-memory speed** | Every read/write hits disk, even for throwaway mid-run data |

### The Solution: Context Objects

Work in fast **in-memory** state during the run.
Only persist to DB **once at the end**, if the run fully succeeded.
Tools stay thin, testable, and decoupled from your storage layer.

---

## Context Objects — The Backpack

### The Mental Model

Think of each agent run as a worker doing a job.
You hand that worker a **backpack** at the start of the job.

The backpack holds everything needed: who they're working for,
what they've done so far, what state they're tracking.

Every tool the agent calls receives that same backpack.
Tools can look inside it and put new things in.
When the run ends, the backpack goes away (unless you save it).

```
Runner.run_sync(agent, "Add milk", context=my_backpack)
                                            ↓
                                  agent calls add_to_cart
                                            ↓
                            add_to_cart receives THE backpack
                            reads cart from backpack
                            writes "milk" back into backpack
                                            ↓
                                  agent calls add_to_cart again
                                            ↓
                            add_to_cart receives THE SAME backpack
                            cart already has "milk" in it from last call
```

**The backpack = context object.**
**The handle you use to open it inside a tool = `RunContextWrapper`.**

### Creating a Context Object

A context object is a **Pydantic `BaseModel`** (or dataclass) with fields
representing the state you need to share across tools.

```python
from pydantic import BaseModel

class ShoppingContext(BaseModel):
    user_name: str              # who is shopping
    items: list[str] = []       # starts empty — tools will fill this
    budget: float = 50.0        # pre-loaded starting value
    spent: float = 0.0          # starts at zero — tools will update this
```

### Key Rule About Context

> **Context is NOT sent to the LLM.**
> It is purely local Python state — your code reads it and writes it.
> The agent can only "see" context through what your tools return to it.

---

## RunContextWrapper — The Handle on the Backpack

### Student Question: *"Why not just pass context directly as a parameter?"*

Because the SDK wraps your context to give you **more than just your data**:

```
RunContextWrapper
├── .context    → YOUR data (ShoppingContext, BankContext, etc.)
└── .usage      → SDK metadata (total_tokens, requests, input_tokens)
```

The `RunContextWrapper` is the SDK's container. Your context is inside it at `.context`.

### Using RunContextWrapper in a Tool

Add it as the **first parameter**. The SDK injects it automatically.
The LLM never sees it — it is excluded from the JSON schema entirely.

```python
from agents import function_tool, RunContextWrapper

@function_tool
def add_item(
    ctx: RunContextWrapper[ShoppingContext],  # position 1 — SDK injects this
    name: str,                                # position 2 — LLM provides this
    price: float                              # position 3 — LLM provides this
) -> str:
    """
    Add an item to the cart if within budget.

    Args:
        name: Item name
        price: Item price in dollars
    """
    if ctx.context.spent + price > ctx.context.budget:
        remaining = ctx.context.budget - ctx.context.spent
        return f"Can't add {name} (${price:.2f}). Only ${remaining:.2f} remaining."

    ctx.context.items.append(name)       # WRITE to backpack
    ctx.context.spent += price           # WRITE to backpack
    return f"Added {name}. Spent: ${ctx.context.spent:.2f} of ${ctx.context.budget:.2f}"
```

### Student Question: *"Why must RunContextWrapper be the first parameter?"*

The SDK detects `RunContextWrapper` by **position (first) and type**.
It then:
1. Excludes it from the JSON schema (LLM never sees it)
2. Injects your context object at runtime automatically

If the LLM tried to fill it in, it would send a random string into
what your code expects to be a structured Python object —
instant crash or silent data corruption.

### Multiple Tools Sharing One Backpack

The real power: multiple tools all reading and writing the
**same backpack** in one run, in sequence.

```python
@function_tool
def add_item(ctx: RunContextWrapper[ShoppingContext], name: str, price: float) -> str:
    """Add an item if within budget. Args: name: item name. price: price in dollars."""
    if ctx.context.spent + price > ctx.context.budget:
        return f"Over budget. Can't add {name}."
    ctx.context.items.append(name)
    ctx.context.spent += price        # Tool 1 writes to backpack
    return f"Added {name} (${price:.2f})"

@function_tool
def show_cart(ctx: RunContextWrapper[ShoppingContext]) -> str:
    """Show current cart and remaining budget."""
    remaining = ctx.context.budget - ctx.context.spent   # Tool 2 reads what Tool 1 wrote
    return f"Cart: {ctx.context.items}\nRemaining budget: ${remaining:.2f}"

@function_tool
def clear_cart(ctx: RunContextWrapper[ShoppingContext]) -> str:
    """Empty the cart and reset spending."""
    count = len(ctx.context.items)
    ctx.context.items = []            # Tool 3 resets what Tools 1 and 2 saw
    ctx.context.spent = 0.0
    return f"Cleared {count} items."
```

All three tools share the same backpack. Changes made by `add_item`
are immediately visible to `show_cart` and `clear_cart`.

---

## Who Creates Context? Can It Start Empty?

### Student Question: *"Who passes the initial data to context?"*

**You** create the context and pass it to the Runner.
That is the only way context gets its initial data.

```python
# YOU create it — with initial data
context = ShoppingContext(user_name="Alice", budget=50.0)

# YOU hand it to the Runner
Runner.run_sync(agent, "Add milk for $3", context=context)
```

The Runner wraps it and passes it to every tool. It never modifies
the initial values — it only delivers the backpack.

### Student Question: *"Can context start empty?"*

Yes. Fields with defaults start at their default value.
Fields without defaults must be provided at creation.

```python
class ShoppingContext(BaseModel):
    user_name: str          # REQUIRED — must provide at creation
    budget: float = 50.0    # optional — has a default
    items: list[str] = []   # starts EMPTY — tools fill this during the run
    spent: float = 0.0      # starts at ZERO — tools update this
```

### Three Common Patterns

```python
# Pattern 1: Pre-loaded — you know the user before the run starts
context = SupportContext(
    customer_id="CUST-42",
    customer_name="Alice",     # fetched from your DB before calling Runner
    account_tier="premium",
    tickets=[],                # starts empty, tools will fill it
)

# Pattern 2: Mostly empty — agent collects data during the run
context = ResearchContext(
    topic="solar energy",      # only the starting prompt
    findings=[],               # tools will populate this
    sources=[],
)

# Pattern 3: All defaults — agent builds entirely from scratch
context = TaskContext()        # all fields have defaults, nothing required
```

> **Rule of thumb:**
> Put in context what you already **know before the run** (user ID, preferences,
> data from your DB). Leave empty what the **tools will discover** during the run.

---

## Agent[TContext] Generics — The Contract

### Student Question: *"What does Agent[ShoppingContext] actually do?"*

At **runtime**: nothing. Python erases generics when code runs.
These two lines are functionally identical:

```python
agent = Agent[ShoppingContext](name="ShopBot", ...)  # runtime: same as below
agent = Agent(name="ShopBot", ...)                   # runtime: same as above
```

What `Agent[ShoppingContext]` gives you:

| Benefit | What It Does |
|---------|-------------|
| **IDE autocomplete** | `ctx.context.` shows all fields of ShoppingContext |
| **Type checker warnings** | Flags wrong context types before you run code |
| **Documentation** | Tells developers what context this agent expects |

### Student Question: *"Does it help in multi-agent systems?"*

Yes — this is where it becomes genuinely valuable.
When agents hand off to other agents, the Runner passes
the **same context object** through the chain.

```python
triage_agent    = Agent[SupportContext](...)  # same type
billing_agent   = Agent[SupportContext](...)  # same type ✓
technical_agent = Agent[SupportContext](...)  # same type ✓
```

If you accidentally use the wrong type, the type checker catches it
**before you run the code**:

```python
billing_agent = Agent[BankContext](...)    # different type!
triage_agent = Agent[SupportContext](
    handoffs=[billing_agent],              # ← type checker flags this:
)                                          # SupportContext ≠ BankContext
```

> **Summary:** `Agent[TContext]` is your compile-time seatbelt.
> The Runner is what actually delivers context to tools.

### Seeing the Generic Catch a Real Error

```python
from pydantic import BaseModel
from agents import Agent, Runner, function_tool, RunContextWrapper

class TaskManagerContext(BaseModel):
    user_id: str
    tasks: list[str] = []

class BankContext(BaseModel):
    account_id: str
    balance: float = 0.0

@function_tool
def add_task(ctx: RunContextWrapper[TaskManagerContext], title: str) -> str:
    """Add a task."""
    ctx.context.tasks.append(title)    # expects .tasks
    return f"Added: {title}"

task_agent = Agent[TaskManagerContext](
    name="TaskManager",
    tools=[add_task],
    instructions="Manage tasks.",
)

# Accidentally pass the WRONG context
bank_ctx = BankContext(account_id="ACC-42", balance=1000.0)

Runner.run_sync(task_agent, "Add a deploy task", context=bank_ctx)
#                                                          ^^^^^^^^
# TYPE CHECKER flags this immediately (red underline in VS Code):
# Argument of type "BankContext" is not assignable to
# parameter expected "TaskManagerContext"
```

Without the generic: no warning, code runs, crashes inside the tool
at runtime with `AttributeError: 'BankContext' object has no attribute 'tasks'`.

---

## How It All Connects — The Office Analogy

This is the best way to see the entire system in one picture.

---

Imagine a company office. A customer calls in with a request.

```
CUSTOMER REQUEST:
"Order 2 laptops, apply my loyalty discount, and send me a confirmation."
```

### The Manager — Runner

The manager receives the call. He opens a **job folder** (context) with
the customer's name, account number, and discount tier written on it.
He hands the folder to the assistant and says *"handle this."*

He does not do the actual work. He coordinates and makes sure
the same folder reaches every person who touches the request.

```python
folder = CustomerContext(name="Alice", account="ACC-42", discount=0.15)
Runner.run_sync(agent, "Order 2 laptops...", context=folder)
```

### The Assistant — Agent

The assistant reads the request and knows which staff members to call
and in what order. She holds the instructions manual (system prompt).
She does not do the actual work herself — she delegates.

```python
agent = Agent[CustomerContext](
    name="Assistant",
    instructions="Handle orders: check stock, apply discounts, send confirmations.",
    tools=[check_stock, apply_discount, send_confirmation],
)
```

### The Staff Members — Tools

Each specialist does exactly one job. When called, they receive
the **job folder** (RunContextWrapper) to see who the customer is
and what has been done so far.

```python
@function_tool
def check_stock(ctx: RunContextWrapper[CustomerContext], product: str, qty: int) -> str:
    """Check and reserve stock. Args: product: product name. qty: quantity."""
    for _ in range(qty):
        ctx.context.items_ordered.append(product)   # write into folder
    return f"Reserved {qty}x {product} for {ctx.context.name}"

@function_tool
def apply_discount(ctx: RunContextWrapper[CustomerContext], unit_price: float) -> str:
    """Calculate total with loyalty discount. Args: unit_price: price per unit."""
    subtotal = unit_price * len(ctx.context.items_ordered)
    discount_amt = subtotal * ctx.context.discount
    ctx.context.final_price = subtotal - discount_amt   # write result to folder
    return f"Total: ${ctx.context.final_price:.2f} (saved ${discount_amt:.2f})"

@function_tool
def send_confirmation(ctx: RunContextWrapper[CustomerContext]) -> str:
    """Send order confirmation email."""
    items = ", ".join(ctx.context.items_ordered)  # read what check_stock wrote
    price = ctx.context.final_price               # read what apply_discount wrote
    return f"Confirmation sent to {ctx.context.name}: [{items}] for ${price:.2f}"
```

### The Job Folder — Context Object

Travels with the request from person to person. Starts with
the customer's basic info. Each staff member reads and writes to it.
By the end it contains the full history of what was done.

```python
class CustomerContext(BaseModel):
    name: str
    account: str
    discount: float
    items_ordered: list[str] = []
    final_price: float = 0.0
```

### The Full Flow

```
Customer calls in
      ↓
Manager (Runner) opens folder (Context), starts the job
      ↓
Assistant (Agent) reads request, decides who to call:
      ↓
  Stock Clerk (check_stock tool)
  → reads ctx.context.name, writes items_ordered to folder
      ↓
  Accounts Clerk (apply_discount tool)
  → reads items_ordered + discount from folder, writes final_price
      ↓
  Comms Clerk (send_confirmation tool)
  → reads name + final_price from folder, sends email
      ↓
Manager (Runner) returns final response
Folder (Context) now holds the full audit trail
```

---

## Complete Working Example — TaskManager

```python
from agents import Agent, Runner, function_tool, RunContextWrapper
from pydantic import BaseModel

# The Job Folder
class TaskManagerContext(BaseModel):
    user_id: str
    current_project: str
    tasks_added: int = 0
    tasks: list[dict] = []

# Tool 1 — Add a task
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

# Tool 2 — List tasks
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

# Tool 3 — Complete a task
@function_tool
def complete_task(ctx: RunContextWrapper[TaskManagerContext], task_id: str) -> str:
    """
    Mark a task as complete.

    Args:
        task_id: The task ID to complete (e.g. 'task_001')
    """
    for task in ctx.context.tasks:
        if task["id"] == task_id:
            task["status"] = "complete"
            return f"Completed {task_id}: '{task['title']}'"
    return f"Task {task_id} not found"

# The Agent
task_manager = Agent[TaskManagerContext](
    name="TaskManager",
    instructions="""You are a task management assistant.
    Help users add, list, and complete tasks.
    Always confirm actions and show the updated list.""",
    tools=[add_task, list_tasks, complete_task],
)

# Run it
context = TaskManagerContext(user_id="dev_42", current_project="Digital FTE MVP")

result = Runner.run_sync(
    task_manager,
    "Add 'Design architecture' (P4) and 'Write tools' (P3). Then list them.",
    context=context,
)
print(result.final_output)

# Run again — same context object, state persists
result = Runner.run_sync(
    task_manager,
    "I finished the architecture. Mark task_001 done.",
    context=context,
)
print(result.final_output)

# Inspect context after the run
print(f"\nAudit: {context.tasks_added} tasks added this session")
```

---

## Progressive Project — Support Desk Assistant

Extend `support_desk.py` from Lesson 1. Build these step by step.

### Step 1 — Context Model

```python
from pydantic import BaseModel

class SupportContext(BaseModel):
    customer_id: str
    customer_name: str
    account_tier: str = "standard"
    tickets: list[dict] = []
```

### Step 2 — Fake Orders Database

```python
ORDERS_DB = {
    "ORD-001": {"product": "Laptop Pro",     "status": "delivered",  "date": "2026-02-10"},
    "ORD-002": {"product": "Wireless Mouse", "status": "in transit", "date": "2026-02-23"},
    "ORD-003": {"product": "USB-C Hub",      "status": "processing", "date": "2026-02-25"},
}
```

### Step 3 — Three Tools to Build

```python
from agents import function_tool, RunContextWrapper

# Tool 1 — No context needed (just reads the DB dict)
@function_tool
def lookup_order(order_id: str) -> str:
    """
    Look up an order by its ID.

    Args:
        order_id: The order ID (e.g. 'ORD-001')
    Returns:
        Order details including product, status, and date
    """
    order = ORDERS_DB.get(order_id)
    if not order:
        return f"Order {order_id} not found."
    return f"Order {order_id}: {order['product']} — {order['status']} (ordered {order['date']})"


# Tool 2 — Context needed (appends to context.tickets)
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
        description: Full description of the problem
        priority: low | medium | high | critical
    Returns:
        Ticket ID and confirmation
    """
    ticket_id = f"TKT-{len(ctx.context.tickets) + 1:04d}"
    ctx.context.tickets.append({
        "id": ticket_id,
        "subject": subject,
        "priority": priority,
        "customer": ctx.context.customer_name,
    })
    return f"Ticket {ticket_id} created: '{subject}' ({priority} priority)"


# Tool 3 — Context needed (reads customer info)
@function_tool
def check_account_status(ctx: RunContextWrapper[SupportContext]) -> str:
    """Return current customer account information and open tickets."""
    return (
        f"Customer: {ctx.context.customer_name} ({ctx.context.customer_id})\n"
        f"Tier: {ctx.context.account_tier}\n"
        f"Open tickets this session: {len(ctx.context.tickets)}"
    )
```

### Step 4 — Wire It Up

```python
from agents import Agent, Runner

support_agent = Agent[SupportContext](
    name="SupportDesk",
    instructions="""You are TechCorp customer support.
    Use your tools to:
    - Look up order status with lookup_order
    - Create support tickets with create_ticket
    - Check account information with check_account_status
    Always confirm actions and ask if there's anything else needed.""",
    tools=[lookup_order, create_ticket, check_account_status],
)

context = SupportContext(
    customer_id="CUST-42",
    customer_name="Alex Chen",
    account_tier="premium",
)

result = Runner.run_sync(
    support_agent,
    "Check my order ORD-002. If it's delayed, create a ticket for me.",
    context=context,
)
print(result.final_output)
```

Run with: `uv run python support_desk.py`

### Success Criteria

- `lookup_order` returns real data from `ORDERS_DB`
- `create_ticket` appends to `context.tickets` and returns a ticket ID
- `check_account_status` reads `customer_name` and `account_tier` from context
- Agent uses all three tools correctly in one conversation

---

## Try It Yourself — Exercises

### Exercise 1 — BankAccount Agent ⭐ (Start Here)

Build a `BankAccount` agent from scratch without looking at previous examples.

**Context model:**
```python
class BankContext(BaseModel):
    owner: str
    balance: float
    transactions: list[str] = []
```

**Three tools to build:**
- `deposit(amount: float)` — adds to balance, appends `"Deposit: +$X"` to transactions
- `withdraw(amount: float)` — subtracts if sufficient funds, appends `"Withdrawal: -$X"`, returns error if insufficient
- `get_statement()` — returns balance and full transaction history

**Test it with:**
```python
context = BankContext(owner="Alice", balance=100.0)
Runner.run_sync(agent, "Deposit $50, withdraw $30, then show my statement", context=context)
```

**Expected output:**
```
Deposited $50.00. New balance: $150.00
Withdrew $30.00. New balance: $120.00

Account Statement for Alice:
Balance: $120.00
Transactions:
  Deposit: +$50.0
  Withdrawal: -$30.0
```

**Things to verify:**
- `withdraw` blocks overdraft attempts with a helpful message
- `get_statement` reads the transactions that `deposit` and `withdraw` wrote
- Context `balance` reflects all changes after the run

---

### Exercise 2 — Inventory Manager ⭐⭐

Build a warehouse inventory agent.

**Context:**
```python
class InventoryContext(BaseModel):
    warehouse: str
    items: dict[str, int] = {}      # item_name → quantity
    low_stock_threshold: int = 10
```

**Tools:**
- `add_stock(item: str, qty: int)` — increases quantity
- `remove_stock(item: str, qty: int)` — decreases quantity, errors if insufficient
- `check_inventory()` — lists all items, flags anything below `low_stock_threshold`

**Test with:** `"Add 50 laptops and 5 mice. Remove 3 laptops. Check what's low on stock."`

---

### Exercise 3 — Quiz Bot ⭐⭐⭐

Build an agent that quizzes a student and tracks their score.

**Context:**
```python
class QuizContext(BaseModel):
    student_name: str
    topic: str
    score: int = 0
    questions_asked: int = 0
    wrong_answers: list[str] = []
```

**Tools:**
- `ask_question(question: str, correct_answer: str, student_answer: str)` — checks answer, updates score
- `give_hint(question: str)` — returns a hint (you make up the hint logic)
- `get_results()` — returns final score, percentage, and list of wrong answers

**Challenge:** The agent should decide which questions to ask based on the topic in context.

---

## Key Takeaways

| Concept | One-liner |
|---------|-----------|
| `@function_tool` | Turns a Python function into an LLM-callable tool |
| Type hints | Define the JSON schema — types and `required` fields |
| Docstring | The tool's description — what the LLM reads to decide when to call it |
| Stateless tools | Functions forget everything between calls — by design |
| Global variables | Shared across all users — never use for agent state |
| Direct DB access | Creates connections, coupling, and concurrency bugs — use context instead |
| `BaseModel` context | Pydantic model holding shared in-memory state for one run |
| `Agent[TContext]` | Type annotation only — no runtime effect, catches type errors in IDE |
| `Runner` | Creates the run, wraps context, delivers it to every tool call |
| `RunContextWrapper` | SDK container injected as first param — `.context` is your data, `.usage` is token metrics |
| Context mutation | Tools write to `ctx.context` — changes persist across all tool calls in the run |
| Who creates context | You do — before calling `Runner.run_sync()` |

---

## What's Next

**Lesson 3 — Agents as Tools & Multi-Agent Orchestration**

Your Support Desk agent currently does everything itself.
In Lesson 3 you'll create specialist sub-agents — a researcher and a writer —
that the main agent can delegate to using `agent.as_tool()`.
You'll also learn when to use `handoff()` instead, and why the choice matters.
