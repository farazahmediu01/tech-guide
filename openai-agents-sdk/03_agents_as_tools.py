from agents import Agent, Runner, RunResult, RunResultStreaming
from pydantic import BaseModel
from clients import gemini_35_flash


# ------------------------------------------------------------------
# Structured output models
# output_type on a sub-agent forces it to return Pydantic, not text.
# The orchestrator then gets clean, predictable data — not a paragraph
# it has to parse.
# ------------------------------------------------------------------

class ResearchOutput(BaseModel):
    topic: str
    key_facts: list[str]     # 3-5 facts a beginner should know
    beginner_analogy: str    # one real-world analogy


class LessonDraft(BaseModel):
    title: str
    objective: str   # one sentence: "By the end, students will..."
    body: str        # 150-200 words
    exercise: str    # one hands-on task


# ------------------------------------------------------------------
# Specialist agents — narrow focus, own tools, own reasoning loop
# ------------------------------------------------------------------

researcher = Agent(
    name="TopicResearcher",
    instructions="""You are a Python/tech education researcher.
    When given a topic, return:
    - 3-5 key facts a beginner student needs to know
    - A simple real-world analogy that explains the concept
    Beginner-friendly language only. No jargon without explanation.""",
    output_type=ResearchOutput,
    model=gemini_35_flash,
)

writer = Agent(
    name="LessonWriter",
    instructions="""You write Python/tech lessons for Aptech students.
    Given research facts and an analogy, produce:
    - A clear lesson title
    - A one-sentence learning objective
    - A short lesson body (150-200 words) using the analogy
    - One practical hands-on exercise students can run immediately
    Simple, direct, no fluff.""",
    output_type=LessonDraft,
    model=gemini_35_flash,
)


# ------------------------------------------------------------------
# Output extractors
# Sub-agents return Pydantic objects. The orchestrator receives a
# string (from tools). Extractors bridge that gap — they convert the
# Pydantic result into a formatted string the manager can read.
# ------------------------------------------------------------------

async def extract_research(result: RunResult | RunResultStreaming) -> str:
    r: ResearchOutput = result.final_output
    facts = "\n".join(f"- {f}" for f in r.key_facts)
    return f"TOPIC: {r.topic}\nFACTS:\n{facts}\nANALOGY: {r.beginner_analogy}"


async def extract_draft(result: RunResult | RunResultStreaming) -> str:
    d: LessonDraft = result.final_output
    return (
        f"TITLE: {d.title}\n"
        f"OBJECTIVE: {d.objective}\n"
        f"BODY:\n{d.body}\n"
        f"EXERCISE: {d.exercise}"
    )


# ------------------------------------------------------------------
# Orchestrator — stays in control, delegates to specialists
# Sees specialist outputs as tool return values (strings), not agents
# ------------------------------------------------------------------

course_manager = Agent(
    name="CourseContentManager",
    instructions="""You manage course content creation for Aptech Python students.
    For every topic request, follow this exact workflow:
    1. Call research_topic to gather facts and an analogy
    2. Call write_lesson using the facts and analogy from step 1
    3. Present the final lesson to the user
    Do not skip steps. Do not write content yourself — delegate it.""",
    tools=[
        researcher.as_tool(
            tool_name="research_topic",
            tool_description="Research a Python/tech topic. Returns key facts and a beginner analogy.",
            custom_output_extractor=extract_research,
        ),
        writer.as_tool(
            tool_name="write_lesson",
            tool_description="Write a structured lesson from research facts. Returns title, objective, body, and exercise.",
            custom_output_extractor=extract_draft,
        ),
    ],
    model=gemini_35_flash,
)


# ------------------------------------------------------------------
# Runners — same pattern as L2, but now the manager orchestrates
# sub-agents internally. You only talk to the manager.
# ------------------------------------------------------------------

# Use case 1: standard topic request
result = Runner.run_sync(
    course_manager,
    "Create a beginner lesson on Python decorators.",
)
print("=== Lesson 1: Decorators ===")
print(result.final_output)

# Use case 2: verify context isolation — each run is independent
result = Runner.run_sync(
    course_manager,
    "Create a beginner lesson on Python Async Context Manager with aiosqlite.",
)
print("\n=== Lesson 2: List Comprehensions ===")
print(result.final_output)
