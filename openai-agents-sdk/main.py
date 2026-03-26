from agents import Agent, Runner, RunContextWrapper, function_tool
from pydantic import BaseModel


class TaskManagerContext(BaseModel):
    user_id: str
    tasks: list[str] = []


class BankContext(BaseModel):
    account_id: int
    balance: float = 0.0


@function_tool
def add_task(ctx: RunContextWrapper[TaskManagerContext], title: str) -> str:
    """
    Adds a task to the current user's task list.
    """
    ctx.context.tasks.append(title)
    return f"Added {title}"


@function_tool
def check_status(ctx: RunContextWrapper[BankContext]) -> str:
    """
    Returns account balance for the current user.
    """

    accout_id = ctx.context.account_id
    balance = ctx.context.balance

    return f"Account {accout_id} has balanace of {balance}"


task_agent = Agent[TaskManagerContext](
    name="TaskManager", instructions="Manage tasks.", tools=[add_task]
)
bank_agent = Agent[BankContext](
    name="BankAgent", instructions="Manage bank accounts.", tools=[check_status]
)

if __name__ == "__main__":
    task_ctx = TaskManagerContext(user_id="user123")
    bank_ctx = BankContext(account_id=12345, balance=1000.0)

    # pass a single agent and context to the runner
    runner_1 = Runner.run_sync(task_agent, "", context=task_ctx)
    runner_2 = Runner.run_sync(bank_agent, "", context=bank_ctx)

    # runner_3= Runner.run_sync(agents=[task_agent, bank_agent], contexts={"TaskManager": task_ctx, "BankAgent": bank_ctx})
