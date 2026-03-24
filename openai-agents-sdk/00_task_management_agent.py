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
    ctx: RunContextWrapper[TaskManagerContext], title: str, priority: int = 1
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
    ctx.context.tasks.append(
        {
            "id": task_id,
            "title": title,
            "priority": priority,
            "status": "pending",
            "project": ctx.context.current_project,
        }
    )
    ctx.context.tasks_added += 1
    return f"Created {task_id}: '{title}' (P{priority})"


# Tool 2 — List tasks
@function_tool
def list_tasks(ctx: RunContextWrapper[TaskManagerContext]) -> str:
    """List all tasks for the current project."""
    tasks = [
        t for t in ctx.context.tasks if t["project"] == ctx.context.current_project
    ]
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
