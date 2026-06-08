from agents import Agent, Runner, RunResult, RunResultStreaming, function_tool, set_tracing_disabled
from pydantic import BaseModel
from clients import gemini_35_flash
from pathlib import Path
from datetime import datetime

set_tracing_disabled(True)  # required when using non-OpenAI models

LESSONS_DIR = Path(__file__).parent / "lessons"


# ------------------------------------------------------------------
# Structured output models
# output_type on a sub-agent forces it to return Pydantic, not text.
# ------------------------------------------------------------------

class ResearchOutput(BaseModel):
    topic: str
    key_facts: list[str]      # 3-5 facts a beginner should know
    beginner_analogy: str     # one real-world analogy
    prerequisites: list[str]  # what students must already understand


class LessonDraft(BaseModel):
    title: str
    objective: str    # "By the end, students will..."
    body: str         # 150-200 words — writer must verify via count_words tool
    exercise: str     # one hands-on task students can run immediately
    word_count: int   # actual count after writer calls count_words


# ------------------------------------------------------------------
# Function tools — real I/O and validation LLMs cannot self-verify
# ------------------------------------------------------------------

@function_tool
def list_existing_lessons() -> list[str]:
    """Return topic slugs already saved as lesson files to avoid duplication."""
    if not LESSONS_DIR.exists():
        return []
    return [f.stem.replace("_", " ") for f in LESSONS_DIR.glob("*.md")]


@function_tool
def count_words(text: str) -> int:
    """Count words in a text block. Use to verify lesson body is 150-200 words."""
    return len(text.split())


@function_tool
def save_lesson_to_markdown(title: str, objective: str, body: str, exercise: str) -> str:
    """Save or update a lesson as a markdown file. Same title slug overwrites existing. Returns the file path."""
    LESSONS_DIR.mkdir(parents=True, exist_ok=True)

    slug = title.lower().replace(" ", "_").replace("/", "_").replace("-", "_")
    filepath = LESSONS_DIR / f"{slug}.md"

    action = "Updated" if filepath.exists() else "Created"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    content = f"""# {title}

**Objective:** {objective}

## Lesson

{body}

## Exercise

{exercise}

---
*{action}: {timestamp}*
"""
    filepath.write_text(content, encoding="utf-8")
    return f"{action} → {filepath}"


# ------------------------------------------------------------------
# Specialist agents — each now has tools grounding their work
# ------------------------------------------------------------------

researcher = Agent(
    name="TopicResearcher",
    instructions="""You are a Python/tech education researcher for Aptech students.

    Workflow:
    1. Call list_existing_lessons — if this topic is already covered, note it and increase depth
    2. Return 3-5 key facts a beginner needs to know
    3. Provide a simple real-world analogy
    4. List 1-3 prerequisites (concepts students must already know)

    Beginner-friendly language only. No jargon without explanation.""",
    tools=[list_existing_lessons],
    output_type=ResearchOutput,
    model=gemini_35_flash,
)

writer = Agent(
    name="LessonWriter",
    instructions="""You write Python/tech lessons for Aptech students.

    Workflow:
    1. Draft the lesson body
    2. Call count_words on your draft — revise until it lands between 150-200 words
    3. Return title, objective, body, exercise, and the verified word_count

    Simple, direct, no fluff. One practical exercise students can run immediately.""",
    tools=[count_words],
    output_type=LessonDraft,
    model=gemini_35_flash,
)


# ------------------------------------------------------------------
# Output extractors — bridge Pydantic sub-agent output → manager string
# IMPORTANT: must be async def + explicit type annotation (SDK requirement)
# ------------------------------------------------------------------

async def extract_research(result: RunResult | RunResultStreaming) -> str:
    r: ResearchOutput = result.final_output
    facts = "\n".join(f"- {f}" for f in r.key_facts)
    prereqs = ", ".join(r.prerequisites) if r.prerequisites else "None"
    return (
        f"TOPIC: {r.topic}\n"
        f"PREREQUISITES: {prereqs}\n"
        f"FACTS:\n{facts}\n"
        f"ANALOGY: {r.beginner_analogy}"
    )


async def extract_draft(result: RunResult | RunResultStreaming) -> str:
    d: LessonDraft = result.final_output
    return (
        f"TITLE: {d.title}\n"
        f"OBJECTIVE: {d.objective}\n"
        f"WORD_COUNT: {d.word_count}\n"
        f"BODY:\n{d.body}\n"
        f"EXERCISE: {d.exercise}"
    )


# ------------------------------------------------------------------
# Orchestrator — delegates all content work, owns file persistence
# ------------------------------------------------------------------

course_manager = Agent(
    name="CourseContentManager",
    instructions="""You manage course content creation for Aptech Python students.

    For every topic request, follow this exact workflow:
    1. Call research_topic to gather facts, analogy, and prerequisites
    2. Call write_lesson using the facts and analogy from step 1
    3. Call save_lesson_to_markdown with the title, objective, body, and exercise from step 2
    4. Present the final lesson to the user and include the saved file path

    Do not skip steps. Do not write content yourself — delegate everything.
    The lesson MUST be saved to disk before you respond.""",
    tools=[
        researcher.as_tool(
            tool_name="research_topic",
            tool_description="Research a Python/tech topic. Returns key facts, analogy, and prerequisites.",
            custom_output_extractor=extract_research,
        ),
        writer.as_tool(
            tool_name="write_lesson",
            tool_description="Write a structured lesson from research. Returns title, objective, body (150-200 words verified), exercise, and word count.",
            custom_output_extractor=extract_draft,
        ),
        save_lesson_to_markdown,
    ],
    model=gemini_35_flash,
)


# ------------------------------------------------------------------
# Run — you only talk to the manager; sub-agents are invisible
# ------------------------------------------------------------------

result = Runner.run_sync(
    course_manager,
    "Create a beginner lesson on Python decorators.",
)
print("=== Lesson 1: Decorators ===")
print(result.final_output)

result = Runner.run_sync(
    course_manager,
    "Create a beginner lesson on Python Async Context Manager with aiosqlite.",
)
print("\n=== Lesson 2: Async Context Manager ===")
print(result.final_output)
