---
marp: true
theme: default
class: invert
style: |
  section { font-size: 22px; }
  section.small { font-size: 18px; }
  section h2 { font-size: 1.4em; }
  section h3 { font-size: 1.1em; }
  pre { font-size: 0.85em; }
---

# Chapter 61.3 — The Agentic Problem-Solving Process
## Student Learning Guide
**Source:** Agent Factory — Panaversity
**URL:** agentfactory.panaversity.org/docs/Building-Agent-Factories/introduction-to-ai-agents

---

## Session Index & Learning Goals

<!-- _class: invert small -->

| # | Topic | You Will Be Able To |
|---|-------|---------------------|
| 1 | Step 1 — Plan | Explain how agents break goals into steps |
| 2 | Step 2 — Act | Describe what a tool call looks like |
| 3 | Step 3 — Observe | Explain what agents do with tool results |
| 4 | Step 4 — Update | Describe how short-term memory gets updated |
| 5 | Step 5 — Evaluate | Explain termination conditions |
| 6 | Full Loop Example | Trace any real agent task end-to-end |
| 7 | Loop in Real Products | Map the loop to tools you already use |

> **Why this matters:** The loop is not just theory — it is the exact execution model used by every production agent. Understanding it deeply means you can debug, improve, and design agents with precision.

---

## The 5-Step Agent Loop

This is the complete problem-solving process every agent follows:

```
┌─────────────────────────────────────────────────┐
│                                                 │
│   GOAL RECEIVED                                 │
│        ↓                                        │
│   Step 1: PLAN                                  │
│        ↓                                        │
│   Step 2: ACT  ──── calls tools                 │
│        ↓                                        │
│   Step 3: OBSERVE ── reads tool results         │
│        ↓                                        │
│   Step 4: UPDATE ─── updates memory/context     │
│        ↓                                        │
│   Step 5: EVALUATE ─ goal met? ──── YES → STOP  │
│        │                                        │
│        └───────── NO → back to Step 1           │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## Step 1 — Plan

### What question does it answer?
*"What is the goal, and what is my first move?"*

Before acting, the agent reasons about the task.

```
Agent receives: "Summarize all customer complaints from last month
                and identify the top 3 recurring issues"

PLAN output:
  1. I need to read the customer complaints database
  2. Filter by last month's date range
  3. Read and process each complaint
  4. Group them by category
  5. Count occurrences
  6. Rank and return top 3

First action: query_database("SELECT * FROM complaints
              WHERE date >= '2026-02-01'")
```

> The plan is not fixed. The agent updates it as it observes results. This is **dynamic planning** — one of the key differences between agents and scripts.

---

## Step 1 — Try It Yourself

Write the initial plan an agent would create for these tasks:

1. *"Find all Python files in this project that import `requests` and list what URLs they call."*

2. *"Check if any student in the database has submitted an assignment but not received a grade."*

3. *"Write a weekly summary email of all support tickets closed this week and send it to the manager."*

**For each plan:**
- What is the first action?
- What tools will be needed?
- What are the logical steps in order?

---

## Step 2 — Act

### What question does it answer?
*"What tool do I call right now to make progress?"*

Acting means calling a tool with specific parameters. This is the only moment the agent interacts with the outside world.

```python
# The agent decides to call this tool:
tool_call = {
    "tool": "query_database",
    "parameters": {
        "sql": "SELECT * FROM complaints WHERE date >= '2026-02-01'"
    }
}

# Other examples of action steps:
tool_call = {"tool": "read_file", "parameters": {"path": "auth.py"}}
tool_call = {"tool": "web_search", "parameters": {"query": "Flask JWT tutorial"}}
tool_call = {"tool": "send_email", "parameters": {"to": "manager@school.com", ...}}
```

> **One action at a time.** Most agents call one tool per loop iteration, observe the result, then decide the next action. This is deliberate — not a limitation.

---

## Step 2 — Try It Yourself

For each situation, write the exact tool call the agent should make:

1. The agent needs to check if a file called `config.py` exists in the project.

2. The agent needs to find all YouTube links in a markdown file called `resources.md`.

3. The agent needs to create a new file called `summary.txt` with the text "Report complete."

4. The agent needs to run the test suite and capture the output.

**Challenge:** An agent is writing a research report. It has finished searching the web and reading 3 articles. What should its next action be? Write the tool call.

---

## Step 3 — Observe

### What question does it answer?
*"What happened as a result of my action?"*

The agent reads the tool's output and interprets it.

```
Action taken: query_database("SELECT * FROM complaints WHERE date >= '2026-02-01'")

Observation:
  Result: 147 rows returned
  Columns: id, customer_id, date, category, description, resolved

  First 3 rows:
  (1, C001, 2026-02-01, "Billing", "Charged twice for same order", True)
  (2, C002, 2026-02-03, "Delivery", "Package arrived damaged", False)
  (3, C001, 2026-02-05, "Billing", "Wrong amount on invoice", True)

Agent interprets:
  "I have 147 complaints. They have categories.
   I should group by category and count to find top issues."
```

> Observation is not passive — the agent actively interprets results and updates its understanding of the task.

---

## Step 3 — What Can Go Wrong Here

<!-- _class: invert small -->

Observation failures are common in real agents. Learn to recognize them.

| Problem | What Happens | How to Fix |
|---------|-------------|-----------|
| Tool returns an error | Agent receives error message, must decide whether to retry or try differently | Build error handling into tool definitions |
| Tool returns empty results | Agent gets zero rows — was the filter too strict? | Agent should reason about why it got no results |
| Tool returns too much data | Agent gets 10,000 rows — context window overflows | Use LIMIT, pagination, or summarization tools |
| Tool returns unexpected format | JSON when text was expected | Validate tool output schemas |
| Tool times out | No response — agent waits forever | Set timeouts and fallback actions |

**The key skill:** Teaching an agent to handle unexpected observations gracefully is what separates demo agents from production agents.

---

## Step 4 — Update

### What question does it answer?
*"What do I now know that I didn't know before? How does this change my plan?"*

After observing, the agent updates its working memory and revises the plan if needed.

```
Previous plan:
  Step 3 (remaining): Group by category → count → rank → return top 3

After observation (147 complaints, category column exists):
  Updated plan:
    - Run: SELECT category, COUNT(*) as count FROM complaints
           WHERE date >= '2026-02-01' GROUP BY category ORDER BY count DESC
    - This single query replaces 3 steps from the original plan
    - Memory updated: "147 complaints, category column confirmed"

New plan is more efficient than original.
```

> **Dynamic planning is what makes agents powerful.** A script runs fixed steps. An agent adapts its plan based on what it discovers.

---

## Step 4 — Try It Yourself

The agent was planning to read 10 files one by one to find a bug. After reading file 3, it finds the bug. What should it do?

1. Continue reading the remaining 7 files as planned
2. Stop the loop immediately and return the result
3. Update the plan — skip remaining files, proceed to fix the bug

**Which is correct? Why?**

---

Now the agent has found and fixed the bug. What does it update in memory before proceeding?

**Think about it:** If this agent has long-term memory and this same bug appears again next month — what should it have stored so it can fix it faster next time?

---

## Step 5 — Evaluate

### What question does it answer?
*"Is the goal complete? Should I stop or loop again?"*

This is the termination decision. The agent checks whether the goal has been achieved.

```
Goal: "Summarize complaints and identify top 3 recurring issues"

Evaluation check:
  ✓ Have I retrieved all complaints?     → Yes (147 rows)
  ✓ Have I grouped and counted?          → Yes (query complete)
  ✓ Have I identified top 3?             → Yes: Billing(52), Delivery(38), Product(27)
  ✓ Have I formatted the summary?        → Yes
  ✓ Is the result complete and correct?  → Yes

Decision: STOP — return result to user

─────────────────────────────────────────────

What if the evaluation fails?

  ✗ "Have I verified the summary is accurate?" → No
  Decision: LOOP — go back to Step 1 with new goal:
            "Verify the summary by cross-checking with raw data"
```

---

## Termination Conditions

<!-- _class: invert small -->

Agents must know when to stop. Without clear termination conditions, agents loop forever.

| Termination Condition | When It Triggers |
|----------------------|-----------------|
| **Goal achieved** | Agent evaluates all criteria as met |
| **Maximum iterations** | Safety limit reached (e.g., after 20 loops) |
| **Error threshold** | Too many consecutive tool failures |
| **Human override** | User cancels the task |
| **Timeout** | Task running too long |
| **Impossible goal detected** | Agent determines the goal cannot be achieved |

> **Always set a max iterations limit.** Without it, a confused agent can run forever (and cost you a fortune in API calls).

---

## Full Loop — End-to-End Example

**Task:** *"Review the student's Python code and provide feedback on correctness and style."*

```
GOAL RECEIVED: Review student code in submission.py

Iter 1:
  PLAN    → "Read the file first"
  ACT     → read_file("submission.py")
  OBSERVE → 47 lines, defines 3 functions, uses loops and conditionals
  UPDATE  → Memory: file read, structure understood

Iter 2:
  PLAN    → "Run the code to check correctness"
  ACT     → run_code("python submission.py")
  OBSERVE → Output matches expected? No — missing edge case for empty list
  UPDATE  → Memory: bug found on line 23

Iter 3:
  PLAN    → "Check style using a linter"
  ACT     → run_linter("submission.py")
  OBSERVE → 3 style warnings: missing docstrings, variable naming
  UPDATE  → Memory: style issues documented

EVALUATE → Have I checked correctness? ✓ Style? ✓
STOP     → Return: feedback report with bug + style notes
```

---

## The Loop Applied to Real Agent Products

<!-- _class: invert small -->

| Agent Product | Goal | Loop Behaviour |
|--------------|------|----------------|
| **Customer Support Agent** | Resolve customer query | Loop until resolved or escalated to human |
| **Code Review Agent** | Review PR for quality | Loop until all files checked and all issues documented |
| **Research Agent** | Write a report on topic X | Loop until enough sources read and report written |
| **Invoice Processing Agent** | Extract and file invoice data | Loop until all fields extracted and filed |
| **Study Assistant Agent** | Help student understand a concept | Loop until student confirms understanding or max turns reached |

> Every one of these is the same 5-step loop — the domain changes, the loop doesn't.

---

## Common Mistakes

| Mistake | Wrong Thinking | Reality |
|---------|---------------|---------|
| "The agent plans once and follows it" | Like a script — fixed steps | Plans are dynamic; updated at every iteration |
| "More loop iterations = better result" | Keep looping for perfection | Stop when goal is met — unnecessary iterations waste money |
| "Observation is automatic" | Tools return results; that's it | The agent must actively interpret what the result means |
| "No termination = no problem" | Agents self-correct eventually | Without termination conditions, agents loop forever |
| "The plan and the goal are the same" | Same thing | Goal = desired outcome. Plan = steps to reach it. Goal is fixed; plan adapts. |
| "The loop is just for complex tasks" | Simple tasks don't need it | Even answering a FAQ question goes through the loop — it just completes in 1 iteration |

---

## Quick Reference Card

```
THE 5-STEP AGENT LOOP

Step 1: PLAN
        What is the goal? What is my first move?
        → Dynamic — updates as new info arrives

Step 2: ACT
        Call exactly one tool with specific parameters
        → The only moment agent touches the outside world

Step 3: OBSERVE
        Read and interpret the tool result
        → Active interpretation, not passive reading

Step 4: UPDATE
        What do I now know? Revise the plan if needed
        → This is what separates agents from scripts

Step 5: EVALUATE
        Is the goal complete?
        → YES: return result and STOP
        → NO:  go back to Step 1 with updated context

TERMINATION CONDITIONS (always define these):
  ✓ Goal achieved
  ✓ Max iterations reached
  ✓ Error threshold exceeded
  ✓ Timeout
  ✓ Human override
```

---

## What's Next — Multi-Agent Design Patterns

You now understand how a single agent solves a problem.

**Next (61.4):** What happens when one agent is not enough?

When tasks are too large, too complex, or require multiple specializations — you need **multiple agents working together**.

There are 4 patterns for multi-agent collaboration:
- **Coordinator** — one agent routes to specialists
- **Sequential** — agents pass results down a pipeline
- **Iterative Refinement** — agents improve each other's output
- **Human-in-the-Loop** — agents pause for human approval

**Preparation question:**
*Think of a task so complex that one agent shouldn't handle it alone — like reviewing a legal contract, or building a full web app. How would you split the work between multiple agents?*
