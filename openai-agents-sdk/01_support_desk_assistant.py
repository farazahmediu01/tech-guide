from enum import StrEnum
from pydantic import BaseModel, Field
from agents import Agent, Runner, function_tool, RunContextWrapper
from clients import gemini_3_flash_preview as gemini_model


class Order(BaseModel):
    id: str
    product: str
    status: str
    date: str

class TicketStatus(StrEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class AccountTier(StrEnum):
    STANDARD = "standard"
    PREMIUM = "premium"


class Ticket(BaseModel):
    id: str
    subject: str
    description: str
    order_id: str | None = None
    status: TicketStatus = Field(
        default=TicketStatus.OPEN, description="The status of the ticket."
    )
    priority: int = Field(
        default=5,
        ge=1,
        le=5,
        description="Ticket priority where 1 is highest and 5 is lowest.",
    )


class SupportContext(BaseModel):
    customer_id: str
    customer_name: str
    account_tier: AccountTier = Field(
        default=AccountTier.STANDARD,
        description="Customer account tier which can be standard or premium.",
    )
    orders: list[Order] = Field(default_factory=list)
    tickets: list[Ticket] = Field(default_factory=list)


@function_tool
def lookup_order(ctx: RunContextWrapper[SupportContext], order_id: str) -> str:
    """
    Lookup an order by its ID.

    Args:
        order_id: The order ID (eg: ORD-001)
    Returns:
        Order details including id, product, status and date.
    """
    for order in ctx.context.orders:
        if order.id == order_id:
            return order.model_dump_json()  
    
    return f"Order with ID: {order_id} not found."


@function_tool
def create_ticket(
    ctx: RunContextWrapper[SupportContext],
    subject: str,
    description: str,
    order_id: str|None = None,
    priority: int = 5,
) -> str:
    """
    Create a support ticket.
    A ticket has a subject, description, order_id, priority and status. The status is set to open when the ticket is created.
    Args:
        subject: The subject of the ticket.
        description: The description of the issue.
        order_id: Optional the id of the order that have an issue.
        priority: The priority of the ticket where 1 is highest and 5 is lowest. Default is 5.
    Returns:
        JSON representation of the created ticket.
    """ 
    if order_id is not None:
        if not any(o.id == order_id for o in ctx.context.orders):
            return f"Order {order_id} not found for this customer." 

    ticket_id = f"Tick-{len(ctx.context.tickets) + 1}"
    ticket = Ticket(
        id=ticket_id,
        subject=subject,
        description=description,
        order_id=order_id,
        status=TicketStatus.OPEN,
        priority=priority,
    )
    ctx.context.tickets.append(ticket)
    return ticket.model_dump_json()


@function_tool
def check_account_status(ctx: RunContextWrapper[SupportContext]) -> str:
    """
    Check the account status of the customer.

    Returns:
        Customer name and id and the account status of the customer which can be standard or premium.
    """

    return f"Customer Name:{ctx.context.customer_name} Customer ID:{ctx.context.customer_id} Account Tier:{ctx.context.account_tier}"


instructions = """
You are a customer support assistant.

Your responsibilities:
- Help customers check order status
- Create support tickets when issues are reported
- Check customer account information

Rules:
- Use the available tools whenever possible instead of guessing.
- If a user asks about an order, use the order lookup tool.
- If the user reports a problem or complaint, create a support ticket.
- If the user asks about account details, check the account status tool.
- Always confirm actions clearly (e.g., ticket created, order found).

Response style:
- Be polite and professional.
- Provide clear and concise responses.
- Include important details such as order IDs, ticket IDs, or account status when available.
"""

support_agent = Agent[SupportContext](
    name="Customer Support Agent",
    instructions=instructions,
    tools=[lookup_order, create_ticket, check_account_status],
    model=gemini_model,
)


support_context_1 = SupportContext(
    customer_id="Customer-001",
    customer_name="Ali",
    orders=[
        Order(id="ORD-001", product="Laptop Pro", status="delivered", date="2026-02-10"),
        Order(id="ORD-002", product="Mouse", status="in transit", date="2026-02-23"),
    ],
)

result_1 = Runner.run_sync(
    starting_agent=support_agent,
    input="create a ticket for my laptop it is broken and not working. order id is ORD-001",
    context=support_context_1,
)

print(result_1.final_output)