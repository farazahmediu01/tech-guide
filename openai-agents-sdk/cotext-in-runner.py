from agents import Agent, Runner, RunContextWrapper, function_tool
from pydantic import BaseModel
from clients import gemini_model


class TaskManagerContext(BaseModel):
    user_id: int | None = None
    current_project: str | None = None
    tasks_added: int = 0


@function_tool
def get_info(ctx: RunContextWrapper[TaskManagerContext]) -> str:
    return ctx.context.model_dump_json()


agent = Agent[TaskManagerContext](
    name="task_manager",
    instructions="you help users to manager thier tasks",
    model=gemini_model,
    tools=[get_info],
)

task_context = TaskManagerContext(user_id=126, current_project="Project Alpha")
result = Runner.run_sync(
    agent,
    "what is the sum of my id? what is the name of this project?",
    context=task_context,
)
print(result.final_output)

# error
# openai.InternalServerError: Error code: 503 - [{'error': {'code': 503, 'message':
# 'This model is currently experiencing high demand. Spikes in demand are usually temporary.
#  Please try again later.', 'status': 'UNAVAILABLE'}}]
