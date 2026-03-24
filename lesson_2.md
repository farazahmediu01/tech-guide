● Full lesson read. Let's build.

  ---
  Lesson 2: Function Tools & Context Objects

  Why this matters: An agent without tools is a chatbot. Tools are what make agents workers — they give your agent hands. And context
   objects are what give those hands memory. Every production agent you'll ever build uses both.

  ---
  Part 1 — The @function_tool Decorator

  The SDK turns any Python function into a tool with one decorator. The key insight: the agent never reads your code — it reads the
  JSON schema generated from your type hints and docstring.

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

  What the SDK generates from your function:

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
      ...

  Becomes this schema the LLM reads:

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

  Three rules for good tools:
  1. Type hints are required — they define the schema types and required fields
  2. Docstring is the tool's API contract — write it as if explaining to a colleague
  3. Optional params get defaults — priority: int = 1 → not in required array

  ---
  Part 2 — Context Objects

  Tools are stateless by default. Each tool call is independent — no shared memory between them. Context objects fix that.

  A context object is a Pydantic BaseModel that holds shared state, passed to every tool, handoff, and agent in a run.

  from pydantic import BaseModel

  class TaskManagerContext(BaseModel):
      user_id: str | None = None
      current_project: str | None = None
      tasks_added: int = 0
      tasks: list[dict] = []

  Wire it to your agent with the generic type Agent[YourContext]:

  from agents import Agent, Runner

  agent = Agent[TaskManagerContext](
      name="TaskManager",
      instructions="Help users manage tasks.",
      tools=[],
  )

  context = TaskManagerContext(user_id="user_123", current_project="Project Alpha")

  result = Runner.run_sync(agent, "What's my current project?", context=context)
  # Output: Your current project is Project Alpha.

  The context is not sent to the LLM — it's purely local state your tools can read and write.

  ---
  Part 3 — RunContextWrapper in Tools

  To access context inside a tool, add RunContextWrapper[YourContext] as the first parameter. The SDK injects it automatically —
  users never provide it.

  from agents import function_tool, RunContextWrapper

  @function_tool
  def add_task(
      ctx: RunContextWrapper[TaskManagerContext],  # ← injected by SDK, not user
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
      ctx.context.tasks_added += 1          # mutate context — persists across calls
      task_id = f"task_{len(ctx.context.tasks) + 1:03d}"
      ctx.context.tasks.append({
          "id": task_id, "title": title,
          "priority": priority, "status": "pending",
          "project": ctx.context.current_project
      })
      return f"Created {task_id}: '{title}' (P{priority})"

  ctx.context → your Pydantic model (read/write)
  ctx.usage → token usage for this run

  ---
  Part 4 — Complete Working Example

  from agents import Agent, Runner, function_tool, RunContextWrapper
  from pydantic import BaseModel

  class TaskManagerContext(BaseModel):
      user_id: str | None = None
      current_project: str | None = None
      tasks_added: int = 0
      tasks: list[dict] = []

  @function_tool
  def add_task(ctx: RunContextWrapper[TaskManagerContext], title: str, priority: int = 1) -> str:
      """Add a task. Args: title: task description. priority: 1-5, 5 is highest."""
      ctx.context.tasks_added += 1
      task_id = f"task_{len(ctx.context.tasks) + 1:03d}"
      ctx.context.tasks.append({"id": task_id, "title": title, "priority": priority, "status": "pending", "project":
  ctx.context.current_project})
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
      """Mark a task complete. Args: task_id: the task ID e.g. task_001."""
      for task in ctx.context.tasks:
          if task["id"] == task_id:
              task["status"] = "complete"
              return f"Completed {task_id}: '{task['title']}'"
      return f"Task {task_id} not found"

  task_manager = Agent[TaskManagerContext](
      name="TaskManager",
      instructions="Help users manage tasks. Add, list, and complete tasks. Always confirm actions.",
      tools=[add_task, list_tasks, complete_task],
  )

  context = TaskManagerContext(user_id="dev_42", current_project="Digital FTE MVP")

  result = Runner.run_sync(
      task_manager,
      "Add: 'Design agent architecture' (P4), 'Write function tools' (P3). Then list them.",
      context=context,
  )
  print(result.final_output)

  ---
  Your Turn — Progressive Project

  Now extend your Support Desk Assistant from Lesson 1. Build support_desk.py in your openai-agents-sdk/ project with:

  Step 1 — Context model:
  class SupportContext(BaseModel):
      customer_id: str
      customer_name: str
      account_tier: str = "standard"
      tickets: list[dict] = []

  Step 2 — Fake orders DB:
  ORDERS_DB = {
      "ORD-001": {"product": "Laptop Pro", "status": "delivered", "date": "2026-02-10"},
      "ORD-002": {"product": "Wireless Mouse", "status": "in transit", "date": "2026-02-23"},
  }

  Step 3 — Three tools to build:
  - lookup_order(order_id: str) — no context needed, just reads ORDERS_DB
  - create_ticket(ctx, subject: str, description: str, priority: str = "medium") — appends to ctx.context.tickets
  - check_account_status(ctx) — reads customer info from context, returns formatted string

  Step 4 — Wire it up:
  support_agent = Agent[SupportContext](
      name="SupportDesk",
      instructions="You are TechCorp support. Use your tools to look up orders, create tickets, and check account status.",
      tools=[lookup_order, create_ticket, check_account_status],
  )

  context = SupportContext(customer_id="CUST-42", customer_name="Alex Chen", account_tier="premium")
  result = Runner.run_sync(support_agent, "Check my order ORD-001 and create a ticket if it's late", context=context)
  print(result.final_output)

  Run with: uv run python support_desk.py

  ---
  Success criteria:
  - lookup_order returns real data from ORDERS_DB
  - create_ticket appends to context.tickets and returns a ticket ID
  - check_account_status reads name and tier from context
  - Agent uses all three tools correctly in one conversation

  ---
  Guiding question before we move on:

  The RunContextWrapper is excluded from the tool's JSON schema — the agent never sees it as a parameter. Why does this matter? What
  would break if the LLM tried to fill in that parameter itself?

  Take a shot at it, then build the Support Desk exercise. Once it's running, we move to Lesson 3 — multi-agent orchestration.

✻ Crunched for 55s