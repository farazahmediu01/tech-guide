from agents import Agent, Runner, RunContextWrapper, function_tool
from pydantic import BaseModel, Field
from clients import gemini_3_flash_preview
from enum import StrEnum


class TaskStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    CANCELLED = "cancelled"


class Task(BaseModel):
    id: int = 0
    title: str
    status: TaskStatus = TaskStatus.PENDING
    project: str
    priority: int = Field(
        default=5, ge=1, le=5, description="1 is highest priority, 5 is lowest"
    )


class TaskManagerContext(BaseModel):
    user_id: int = 0  # currently unused fileds.
    project: str
    task_counter: int = 0
    tasks: list[Task] = Field(default_factory=list)


@function_tool
def add_task(
    ctx: RunContextWrapper[TaskManagerContext], title: str, priority: int = 5
) -> str:
    """
    Add a new task to the current user's task list.

    Args:
        title name of the task to be added.
        priority (1 = highest, 5 = lowest).

    Returns:
        A Confirmation message with that the task was successfully aded with task name and id.
    """
    ctx.context.task_counter += 1
    task = Task(
        id=ctx.context.task_counter,
        title=title,
        priority=priority,
        project=ctx.context.project,
    )
    ctx.context.tasks.append(task)
    return f"Task added id:{task.id} title:{task.title} priority:{task.priority}"


@function_tool
def list_tasks(ctx: RunContextWrapper[TaskManagerContext], limit: int = 5) -> str:
    """List all tasks for the current project."""
    tasks = [t for t in ctx.context.tasks if t.project == ctx.context.project]
    if not tasks:
        return f"No tasks for '{ctx.context.project}'"
    # completed_tasks = [t for t in tasks if t.status == TaskStatus.complete]

    lines = [f"Tasks for Project: {ctx.context.project}"]
    for t in tasks[:limit]:
        msg = f"{t.id} {t.title.title()} {t.priority} {t.status.title()}"
        lines.append(msg)

    return "\n".join(lines)


# should i use task title or task id to seach?
@function_tool
def complete_task(ctx: RunContextWrapper[TaskManagerContext], title: str) -> str:
    """
    Mark a task as complete by title. Note: use task_id for production..
    Args:
        title: Task name to complete (e.g. 'task_001')
    """
    for task in ctx.context.tasks:
        if task.title == title:
            task.status = TaskStatus.COMPLETE
            return f"Task completed id:{task.id} title:{task.title} priority:{task.priority}"
    return f"Task with title: {title} not found."


task_manager = Agent[TaskManagerContext](
    name="TaskManager",
    instructions="""You are a task management assistant.
    Help users add, list, and complete tasks.
    Always confirm actions and show the updated list.""",
    tools=[add_task, list_tasks, complete_task],
    model=gemini_3_flash_preview,
)

context = TaskManagerContext(project="Digital FTE MVP")

result = Runner.run_sync(
    task_manager,
    "Add 'Design architecture' (P4) and 'Write tools' (P3). Then list them.",
    context=context,
)
print(result.final_output)


result = Runner.run_sync(
    task_manager, "I finished the architecture design. Mark it done.", context=context
)
print(result.final_output)
