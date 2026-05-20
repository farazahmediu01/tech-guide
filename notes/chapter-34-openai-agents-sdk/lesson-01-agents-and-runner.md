# Lesson 1: Agents & Runner — Core Primitives

> **Chapter:** 34 — OpenAI Agents SDK
> **Last Updated:** 2026-04-02
> **Skill reference:** `/mnt/c/Users/Faraz/.claude/skills/openai-agents-sdk/references/core-primitives.md`

---

## Table of Contents

1. [The Big Picture](#the-big-picture)
2. [What Is an AI Agent?](#what-is-an-ai-agent)
3. [The Agent Class — The Blueprint](#the-agent-class--the-blueprint)
4. [Agent Parameters Deep Dive](#agent-parameters-deep-dive)
5. [Dynamic Instructions — Context-Aware System Prompts](#dynamic-instructions--context-aware-system-prompts)
6. [The Runner — The Execution Engine](#the-runner--the-execution-engine)
7. [The Agent Run Loop — What Happens Inside](#the-agent-run-loop--what-happens-inside)
8. [max_turns and Stopping Conditions](#max_turns-and-stopping-conditions)
9. [RunResult — What Comes Back](#runresult--what-comes-back)
10. [Async vs Sync — Which One to Use](#async-vs-sync--which-one-to-use)
11. [Model Configuration](#model-configuration)
12. [Environment Setup](#environment-setup)
13. [Complete Working Example](#complete-working-example)
14. [Try It Yourself — Exercises](#try-it-yourself--exercises)
15. [Key Takeaways](#key-takeaways)
16. [What's Next](#whats-next)

---

## The Big Picture

> **One sentence:** An agent is a loop — think, decide, act, repeat — until the job is done.

Most developers build chatbots: the user sends a message, the LLM replies, done.
Agents are different. They can decide to use tools, call them, read the results, decide
what to do next, call more tools — all without asking the user again.

The OpenAI Agents SDK gives you three primitives to build this:

| Primitive | What It Is | Analogy |
|-----------|-----------|---------|
| `Agent` | The blueprint — instructions + tools | A job description |
| `Runner` | The execution engine — runs the loop | A manager who executes the job |
| `RunResult` | The output — everything that happened | The completed work report |

Everything else in the SDK (tools, context, guardrails, memory, multi-agent) builds
on top of these three. If you understand them deeply, everything else is just configuration.

---

## What Is an AI Agent?

### Student Question: *"What's the difference between a chatbot, a script, and an agent?"*

| | Chatbot | Script | Agent |
|---|---------|--------|-------|
| **Decides what to do?** | No — just responds | No — hardcoded steps | Yes — chooses its own path |
| **Uses tools?** | No | Yes (hardcoded order) | Yes (decides order dynamically) |
| **Handles unexpected input?** | Sometimes | No — crashes or ignores | Yes — adapts |
| **Example** | ChatGPT (no tools) | `python scrape.py` | Customer support agent that looks up orders, creates tickets, escalates when needed |

### The Three Signs Something Is an Agent

1. **Autonomy** — it decides which steps to take, not you
2. **Tool use** — it can act on the world, not just talk about it
3. **Loop** — it can take multiple steps before finishing

### Why This Matters for Your Digital FTE Goal

A Digital FTE (your end goal) is an agent that replaces a human worker.
A human worker doesn't wait for instructions on every single step.
They receive a goal, figure out the steps, take actions, and report back.
That is exactly what an agent does.

---

## The Agent Class — The Blueprint

The `Agent` class defines everything about what an agent is and what it can do.
It does **not** run anything — that's the Runner's job.

```python
from agents import Agent

agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant.",
)
```

This is the minimum. `name` and `instructions` are all you need to start.
Everything else is optional.

### Full Constructor

```python
from agents import Agent

agent = Agent[TContext](
    name="SupportDesk",                  # Required — used in logs and multi-agent handoffs
    instructions="You are...",           # Required — the system prompt
    model="gpt-4o",                      # Optional — defaults to gpt-4o
    tools=[],                            # Optional — @function_tool, FileSearchTool, etc.
    handoffs=[],                         # Optional — other agents to transfer to
    input_guardrails=[],                 # Optional — validate input before LLM sees it
    output_guardrails=[],                # Optional — validate output before returning
    output_type=None,                    # Optional — Pydantic model for structured output
    mcp_servers=[],                      # Optional — external tool servers
    model_settings=None,                 # Optional — temperature, max_tokens, etc.
)
```

> **Important:** Creating an `Agent` object costs nothing.
> No API call is made until you pass it to `Runner.run()`.
> You can create 10 agents and only run 1 — that's fine.

---

## Agent Parameters Deep Dive

### `name`

Used in two places:
1. Tracing and logs — you'll see this name in the OpenAI dashboard when debugging
2. Multi-agent systems — when one agent hands off to another, the name identifies who's running

```python
# Good name: describes what the agent does
agent = Agent(name="OrderLookupSpecialist", ...)

# Bad name: generic and unhelpful in logs
agent = Agent(name="agent1", ...)
```

### `instructions`

This is the **system prompt** — the agent's personality, role, and rules.
Everything you put here shapes how the agent reasons and what it focuses on.

```python
agent = Agent(
    name="SupportDesk",
    instructions="""You are TechCorp customer support.
    
    Your priorities:
    1. Look up order status before assuming there's a problem
    2. Create a ticket for any issue you can't resolve immediately
    3. Escalate to a human agent for refunds over $500
    
    Always confirm actions before taking them.
    Always end by asking if there's anything else needed.""",
)
```

Write instructions like you're onboarding a new employee.
Vague instructions produce unpredictable behavior.
Specific instructions produce reliable behavior.

### `model`

The model string is passed directly to the OpenAI API by default.
You can also pass a `Model` instance to use non-OpenAI providers (covered in [Model Configuration](#model-configuration)).

```python
# 1. Simple chat agent — greets users, answers FAQs
agent = Agent(
    name="FAQBot",
    instructions="Answer common questions about our product. Be concise and friendly.",
    model="gpt-4o-mini",    # Fast and cheap — perfect for simple Q&A
)

# 2. Requires deeper thinking — legal clause analysis
agent = Agent(
    name="ContractAnalyst",
    instructions="Analyze legal contracts. Identify risks, obligations, and ambiguous clauses.",
    model="o3-mini",        # Reasoning model — thinks step by step before answering
)

# 3. Works with images — product photo quality checker
agent = Agent(
    name="ProductPhotoReviewer",
    instructions="Review product photos. Check lighting, background, and image quality. Flag issues.",
    model="gpt-4o",         # Vision-capable — can read and describe images
)

# 4. Works with audio — meeting transcription summarizer
agent = Agent(
    name="MeetingSummarizer",
    instructions="Listen to meeting audio. Produce a structured summary with action items.",
    model="gpt-4o-audio-preview",  # Audio-capable — accepts audio input directly
)
```

In a multi-agent system, assign the cheapest model that can do the job:

```python
triage_agent   = Agent(name="Triage",   ..., model="gpt-4o-mini")  # just routing — keep it cheap
research_agent = Agent(name="Research", ..., model="gpt-4o")        # deep analysis — needs power
```

### `output_type`

By default, `result.final_output` is a plain string.
If you set `output_type`, the agent is forced to return a structured Pydantic object.

**Example — Chef agent that returns a structured recipe:**

```python
from pydantic import BaseModel
from agents import Agent, Runner

class Recipe(BaseModel):
    dish_name: str
    cuisine: str
    prep_time_minutes: int
    ingredients: list[str]
    difficulty: str   # "easy" | "medium" | "hard"

chef_agent = Agent(
    name="ChefAdvisor",
    instructions="""You are a professional chef.
    When given a list of ingredients, suggest one recipe that uses them.
    Be practical — suggest dishes a home cook can actually make.""",
    output_type=Recipe,
)

result = Runner.run_sync(
    chef_agent,
    "I have chicken, garlic, lemon, and rosemary. What can I make?"
)

recipe = result.final_output        # Recipe object — not a plain string
print(recipe.dish_name)             # "Lemon Rosemary Roasted Chicken"
print(recipe.prep_time_minutes)     # 15
print(recipe.difficulty)            # "easy"
print(recipe.ingredients)           # ["chicken thighs", "garlic", "lemon", "rosemary", "olive oil"]
```

Without `output_type`, the agent might reply:
> *"You could make Lemon Rosemary Chicken! It takes about 15 minutes to prep..."*

With `output_type`, you get a Python object your code can actually work with —
save it to a database, render it in a UI, pass it to another agent.

> **When to use `output_type`:**
> When downstream code needs to process the output programmatically
> (store in DB, render in UI, feed into another workflow).
> When you just need a conversational reply, leave it as `None`.

### `model_settings`

Fine-tune how the model behaves:

```python
from agents import ModelSettings

agent = Agent(
    name="Precise",
    instructions="Extract data exactly as provided — do not infer or guess.",
    model_settings=ModelSettings(
        temperature=0.0,    # 0 = deterministic/precise, 1 = creative/varied
        max_tokens=500,     # cap response length
    ),
)
```

> **Warning: Not all `ModelSettings` fields work with every model.**
>
> | Setting | OpenAI GPT-4o | o3-mini (reasoning) | Gemini / Ollama |
> |---------|:---:|:---:|:---:|
> | `temperature` | ✅ | ❌ fixed internally | ⚠️ varies by provider |
> | `max_tokens` | ✅ | ✅ | ⚠️ varies by provider |
> | `top_p` | ✅ | ❌ | ⚠️ varies by provider |
>
> Reasoning models (`o3-mini`, `o1`) control their own temperature — passing it is silently ignored or raises an error.
> When using Gemini or Ollama, check that provider's documentation for which settings are supported.
> **When in doubt: only set what you need and test it.**

---

## Dynamic Instructions — Context-Aware System Prompts

### Student Question: *"What if the system prompt needs to change based on who's using the agent?"*

Instead of a static string, pass a **function** as `instructions`.
The SDK calls this function fresh on every run, with access to the context object.

```python
from agents import Agent, RunContextWrapper
from pydantic import BaseModel

class CustomerContext(BaseModel):
    customer_name: str
    account_tier: str     # "standard" | "premium" | "vip"
    language: str = "en"

def build_instructions(ctx: RunContextWrapper[CustomerContext], agent: Agent) -> str:
    tier = ctx.context.account_tier
    name = ctx.context.customer_name

    base = f"You are TechCorp support. You are helping {name}."

    if tier == "vip":
        return base + " VIP customers get priority handling and direct escalation paths."
    elif tier == "premium":
        return base + " Premium customers get extended return windows (60 days)."
    else:
        return base + " Standard return policy applies (30 days)."

agent = Agent[CustomerContext](
    name="SupportDesk",
    instructions=build_instructions,   # function, not string
    tools=[...],
)
```

Every call to `Runner.run()` with a different context will produce a different system prompt.
Same agent class, personalized behavior per user.

---

## The Runner — The Execution Engine

The `Runner` is what actually executes the agent loop.
You never create a `Runner` instance — you call its class methods directly.

### Three Methods

| Method | When to Use |
|--------|-------------|
| `await Runner.run(agent, input)` | **Default for production** — async, non-blocking |
| `Runner.run_sync(agent, input)` | Scripts, tests, notebooks — blocks until done |
| `Runner.run_streamed(agent, input)` | When you need to stream tokens as they arrive |

### Full Signature

```python
result = await Runner.run(
    starting_agent=agent,         # The agent to start with
    input="User message here",    # str or list of message dicts
    context=my_context,           # Your context object (optional)
    session=SQLiteSession("id"),  # For conversation memory (optional)
    run_config=RunConfig(         # Tracing config (optional)
        workflow_name="SupportWorkflow",
    ),
    max_turns=10,                 # Safety cap on the loop (default: 10)
)
```

### What the Runner Actually Does

The Runner is not magic — it's a loop:

```
1. Send the input + instructions to the LLM
2. Get a response
3. If response = "call this tool" → call the tool, add result to messages → go to step 1
4. If response = "here is the final answer" → stop, return RunResult
```

That's it. The LLM decides whether to call tools or respond. The Runner just obeys and keeps the loop going.

---

## The Agent Run Loop — What Happens Inside

This is the most important thing to understand about agents.

```
User sends: "Check my order ORD-002 and create a ticket if it's delayed"
                                    ↓
Runner sends: [system prompt] + [user message] → LLM
                                    ↓
LLM decides: "I should call lookup_order first"
                                    ↓
Runner calls: lookup_order("ORD-002") → "in transit since 3 weeks ago"
                                    ↓
Runner sends: [system prompt] + [user message] + [tool call] + [tool result] → LLM
                                    ↓
LLM decides: "Order is delayed. I should call create_ticket"
                                    ↓
Runner calls: create_ticket(subject="Delayed order ORD-002", priority="medium")
                                    ↓
Runner sends: [all messages so far] + [new tool result] → LLM
                                    ↓
LLM decides: "I have enough info to respond to the user"
                                    ↓
Runner returns: RunResult with final_output = "Your order is delayed...ticket TKT-0001 created."
```

### Key Insight: The LLM Sees the Whole History

Every time the loop goes around, the LLM receives the **full conversation history**:
original message + every tool call + every tool result + every previous LLM response.

This is why agents can reason across multiple steps — they're not forgetting anything.
It's also why longer runs cost more tokens.

---

## max_turns and Stopping Conditions

### Student Question: *"What if the agent gets stuck in an infinite loop?"*

`max_turns` is your safety net. Default is **10**.

```python
result = await Runner.run(agent, "...", max_turns=5)
```

One "turn" = one LLM call. Counting tool calls is separate.

### When the Loop Stops

The agent loop ends when any of these happen:

| Condition | What Happens |
|-----------|-------------|
| LLM produces a final text response | Normal completion — `result.final_output` has the answer |
| LLM produces a structured output (if `output_type` set) | Normal completion — `result.final_output` is a typed object |
| `max_turns` is reached | `MaxTurnsExceeded` exception is raised |
| A guardrail triggers | `InputGuardrailTripwireTriggered` or `OutputGuardrailTripwireTriggered` |
| A handoff occurs | Control transfers to another agent, loop continues there |

### Handling max_turns in Production

```python
from agents import Runner, MaxTurnsExceeded

try:
    result = await Runner.run(agent, user_input, max_turns=10)
    return result.final_output
except MaxTurnsExceeded:
    return "I wasn't able to complete this in time. Please try a simpler request."
```

> **Rule of thumb for max_turns:**
> Simple agents (1-2 tools): `max_turns=5`
> Multi-step workflows: `max_turns=10` (default)
> Complex research agents: `max_turns=20`
> Never set it to 0 or very high values in production.

---

## RunResult — What Comes Back

```python
result = await Runner.run(agent, "What time is it?")

result.final_output          # The agent's final answer (str or Pydantic object)
result.last_agent            # Which agent produced the final response (matters in multi-agent)
result.new_items             # Every message and tool call that happened during the run
result.input                 # The original input you passed in
```

### Inspecting What Happened

```python
result = Runner.run_sync(agent, "Check order ORD-001 and create a ticket")

print(result.final_output)   # The answer given to the user

# See every step the agent took
for item in result.new_items:
    print(type(item).__name__, "→", item)
```

### Using Structured Output

```python
from pydantic import BaseModel
from agents import Agent, Runner

class TicketSummary(BaseModel):
    ticket_id: str
    priority: str

agent = Agent(
    name="Extractor",
    instructions="Extract ticket info.",
    output_type=TicketSummary,
)

result = Runner.run_sync(agent, "Create a high priority ticket for login failure")
ticket = result.final_output       # TicketSummary object
print(ticket.ticket_id)            # "TKT-0001"
print(ticket.priority)             # "high"
```

---

## Async vs Sync — Which One to Use

### Student Question: *"When do I use run_sync vs run?"*

```python
# run_sync — blocks. Simple. Use in:
#   - standalone scripts
#   - Jupyter notebooks
#   - tests
result = Runner.run_sync(agent, "Hello")

# run (async) — non-blocking. Use in:
#   - FastAPI/web servers (MUST use this)
#   - any async application
#   - production code
import asyncio

async def main():
    result = await Runner.run(agent, "Hello")
    print(result.final_output)

asyncio.run(main())
```

### Why This Matters for Real Projects

If you're building a web API (which you will), every request handler is async.
Calling `run_sync` inside an async function will **block the entire server** —
no other requests can be handled while one agent is running.

```python
# WRONG — blocks the entire FastAPI server
@app.post("/chat")
async def chat(msg: str):
    result = Runner.run_sync(agent, msg)   # ❌ blocks all other requests
    return result.final_output

# CORRECT
@app.post("/chat")
async def chat(msg: str):
    result = await Runner.run(agent, msg)  # ✅ non-blocking
    return result.final_output
```

> **Default rule:** Always write `async def` + `await Runner.run()`.
> Only drop to `run_sync` for quick scripts and tests.

---

## Model Configuration

### Choosing the Right Model

See the `model` parameter section above for 4 real-world agent examples.
Quick reference:

| Use Case | Model | Why |
|----------|-------|-----|
| FAQ bots, routing, simple chat | `gpt-4o-mini` | Fast and cheap |
| Analysis, code generation, complex tasks | `gpt-4o` | Best general capability |
| Multi-step reasoning, math, logic | `o3-mini` | Thinks before it answers |
| Vision tasks (images, screenshots) | `gpt-4o` | Natively vision-capable |
| Audio input/output | `gpt-4o-audio-preview` | Accepts and generates audio |

### Using Non-OpenAI Models

The SDK wraps any OpenAI-compatible API. The pattern is always the same:
1. Create an `AsyncOpenAI` client pointing to the provider's base URL
2. Wrap it in `OpenAIChatCompletionsModel`
3. Pass that as the `model` to your `Agent`

**Google Gemini** (from your working `clients.py`):

```python
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, set_tracing_disabled
from dotenv import load_dotenv
import os

load_dotenv()

# Step 1 — Must disable tracing when using non-OpenAI providers
set_tracing_disabled(True)

# Step 2 — Create a client pointing to Gemini's OpenAI-compatible endpoint
gemini_client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# Step 3 — Wrap in OpenAIChatCompletionsModel
gemini_3_flash = OpenAIChatCompletionsModel(
    openai_client=gemini_client,
    model="gemini-3-flash-preview",
)

# Step 4 — Pass to Agent
agent = Agent(
    name="GeminiAssistant",
    instructions="You are a helpful assistant.",
    model=gemini_3_flash,   # Model instance, not a string
)
```

**Local Ollama (free, runs offline):**

```python
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, set_tracing_disabled

set_tracing_disabled(True)  # Required for non-OpenAI providers

ollama_client = AsyncOpenAI(
    api_key="ollama",                       # placeholder — Ollama doesn't need a real key
    base_url="http://localhost:11434/v1",   # Ollama's local server
)

llama = OpenAIChatCompletionsModel(
    openai_client=ollama_client,
    model="llama3.2",
)

agent = Agent(name="LocalAgent", instructions="Be helpful.", model=llama)
```

> **Why `set_tracing_disabled(True)`?**
> The SDK's tracing system sends run data to OpenAI's platform.
> Non-OpenAI providers can't receive this data — it will error.
> Always call `set_tracing_disabled(True)` before running agents on Gemini or Ollama.

### ModelSettings — Fine-Tuning Behavior

```python
from agents import ModelSettings

agent = Agent(
    name="DataExtractor",
    instructions="Extract structured data exactly as provided.",
    model_settings=ModelSettings(
        temperature=0.0,     # Lower = more deterministic
        max_tokens=1000,     # Cap output length
    ),
)
```

| Setting | What It Does | When to Change |
|---------|-------------|----------------|
| `temperature` | Randomness (0.0–2.0, default ~1.0) | Lower for extraction/classification; higher for creative writing |
| `max_tokens` | Max output length | Set when you need to control cost or response length |

> **Reminder:** Not all settings work with all models. See the warning under `model_settings` above.

---

## Environment Setup

```bash
# Create project
uv init my-agent-project --python 3.12
cd my-agent-project

# Add dependencies
uv add openai-agents python-dotenv
```

**`.env` file (never commit this):**
```
OPENAI_API_KEY=sk-...
```

**Load in your code:**
```python
from dotenv import load_dotenv
load_dotenv()   # reads .env file into environment variables

# The SDK reads OPENAI_API_KEY from environment automatically
# Never do: Agent(api_key="sk-...") — that would expose your key in code
```

**`.gitignore` (always include):**
```
.env
__pycache__/
.venv/
```

---

## Complete Working Example

This example uses every core primitive from this lesson.

```python
import asyncio
import os
from pydantic import BaseModel
from dotenv import load_dotenv
from agents import Agent, Runner, ModelSettings

load_dotenv()

# --- Structured output model ---
class MovieRecommendation(BaseModel):
    title: str
    year: int
    genre: str
    reason: str   # Why this matches the user's request

# --- Agent definition ---
movie_agent = Agent(
    name="MovieAdvisor",
    instructions="""You are a knowledgeable film critic and recommender.
    When a user describes what they want to watch, recommend exactly one movie.
    Be specific about why it matches their request.
    Only recommend real movies that exist.""",
    model="gpt-4o-mini",
    model_settings=ModelSettings(temperature=0.7),
    output_type=MovieRecommendation,
)

# --- Async runner (production default) ---
async def get_recommendation(user_request: str) -> MovieRecommendation:
    result = await Runner.run(
        movie_agent,
        user_request,
        max_turns=3,
    )
    return result.final_output  # typed MovieRecommendation object

# --- Entry point ---
async def main():
    requests = [
        "I want something funny with a surprise ending",
        "Show me a sci-fi film about AI going wrong",
    ]

    for req in requests:
        print(f"\nRequest: {req}")
        movie = await get_recommendation(req)
        print(f"  Title:  {movie.title} ({movie.year})")
        print(f"  Genre:  {movie.genre}")
        print(f"  Why:    {movie.reason}")

asyncio.run(main())
```

**Run with:** `uv run python main.py`

**What this demonstrates:**
- `Agent` with all relevant parameters
- `output_type` returning a typed Pydantic object
- `ModelSettings` with custom temperature
- `async/await` with `Runner.run()`
- `max_turns` safety cap
- Accessing `.final_output` as a typed object

---

## Try It Yourself — Exercises

### Exercise 1 — Hello Agent ⭐ (Start Here)

Build the simplest possible agent from scratch without looking at the examples above.

**Requirements:**
- Agent named `"Greeter"` that introduces itself when asked
- Run it with `Runner.run_sync()`
- Print `result.final_output`

**Test with:** `"Who are you and what can you help me with?"`

---

### Exercise 2 — Structured Output ⭐⭐

Build an agent that reads a job posting and extracts structured data.

**Pydantic model to use:**
```python
class JobPosting(BaseModel):
    company: str
    role: str
    required_skills: list[str]
    is_remote: bool
    experience_years: int
```

**Test with:**
```
"We're hiring a Senior Python Engineer at TechCorp (remote).
5+ years experience required. Must know FastAPI, Docker, and PostgreSQL."
```

**Verify:** `result.final_output` is a `JobPosting` object with correct fields.

---

### Exercise 3 — Async + max_turns ⭐⭐

Rewrite Exercise 1 using `async def main()` and `await Runner.run()`.
Set `max_turns=2`.

Then test what happens when you set `max_turns=0`.

> **Think about it:** What error do you get? Where in your code should you catch it?

---

### Exercise 4 — Dynamic Instructions ⭐⭐⭐

Build an agent whose system prompt changes based on user data.

**Context model:**
```python
class UserContext(BaseModel):
    username: str
    is_premium: bool
```

**Instructions function:**
- If `is_premium=True`: agent mentions premium features and offers priority support
- If `is_premium=False`: agent mentions the free tier limitations and upgrade offer

**Test with two different contexts** and verify the agent responds differently.

---

### Exercise 5 — Model Comparison ⭐⭐⭐

Build the same agent twice — one with `gpt-4o-mini`, one with `gpt-4o`.
Give both a complex reasoning question.
Compare the responses and note the difference in quality and token usage.

> **Challenge:** How would you measure which model is more cost-effective for this task?

---

## Key Takeaways

| Concept | One-liner |
|---------|-----------|
| `Agent` | Blueprint only — defines what the agent is and can do, costs nothing to create |
| `instructions` | The system prompt — be specific; vague instructions = unpredictable behavior |
| `name` | Required for readable logs and multi-agent systems |
| `output_type` | Forces structured Pydantic output — use when downstream code needs to parse the result |
| `model_settings` | Fine-tunes LLM behavior — `temperature=0` for extraction, higher for creativity |
| `Runner` | Executes the agent loop — you never instantiate it, just call its class methods |
| `Runner.run()` | Async — default for all production code and web servers |
| `Runner.run_sync()` | Sync — scripts and tests only; blocks the thread |
| Agent run loop | Think → decide (tool or respond?) → act → repeat until final answer |
| `max_turns` | Safety cap on the loop — always set this in production (default 10) |
| `MaxTurnsExceeded` | Exception raised when loop cap is hit — always catch this in production |
| `RunResult.final_output` | The agent's final answer — `str` by default, typed object if `output_type` set |
| `RunResult.last_agent` | Which agent responded — matters in multi-agent handoff chains |
| Dynamic instructions | Pass a function instead of a string — called fresh every run with context access |
| `set_tracing_disabled(True)` | Required when using non-OpenAI models (Gemini, Ollama) |

---

## What's Next

**Lesson 2 — Function Tools & Context Objects**

Your movie agent and greeter agent can only talk.
In Lesson 2 you'll give agents hands — tools that let them act on the world.
You'll also learn how to share state across multiple tool calls within one run
using context objects and `RunContextWrapper`.

> **Preparation question:** If a tool is just a Python function, what information
> does the agent need in order to know when to call it and what arguments to pass?
