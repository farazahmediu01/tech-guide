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

# Chapter 61.4 — Multi-Agent Design Patterns
## Student Learning Guide
**Source:** Agent Factory — Panaversity
**URL:** agentfactory.panaversity.org/docs/Building-Agent-Factories/introduction-to-ai-agents

---

## What You Will Learn

By the end of this guide you will be able to:

- Explain why one agent is sometimes not enough
- Describe all 4 multi-agent design patterns with real examples
- Choose the right pattern for a given problem
- Trace a task through each pattern step by step
- Identify which pattern Claude Code itself uses internally

> **Why this matters:** Every production-grade Digital FTE you will build or sell will use at least one of these patterns. This is where single agents become powerful systems.

---

## Why Multi-Agent Systems?

A single agent has limits:

```
Problem 1: Context Window
  A single agent can only hold so much information at once.
  A 100-file codebase audit overwhelms one agent.

Problem 2: Specialization
  One agent cannot be an expert in everything.
  A legal review + financial analysis + risk assessment
  requires different expertise.

Problem 3: Parallelism
  One agent works sequentially.
  Three agents can work simultaneously — 3x faster.

Problem 4: Quality Control
  The same agent that writes output also reviews it.
  Blind spot problem — it misses its own mistakes.
```

**Solution: Multiple agents, each doing what it does best.**

---

## The 4 Multi-Agent Design Patterns

```
┌──────────────────────────────────────────────────┐
│                                                  │
│  Pattern 1: COORDINATOR                          │
│  One agent routes tasks to specialists           │
│                                                  │
│  Pattern 2: SEQUENTIAL                           │
│  Each agent's output feeds the next              │
│                                                  │
│  Pattern 3: ITERATIVE REFINEMENT                 │
│  Agents loop to improve quality                  │
│                                                  │
│  Pattern 4: HUMAN-IN-THE-LOOP                    │
│  Agent pauses for human approval                 │
│                                                  │
└──────────────────────────────────────────────────┘
```

These are not mutually exclusive. Real systems combine multiple patterns.

---

## Pattern 1 — Coordinator

### What question does it answer?
*"How do I route different types of tasks to the right specialist?"*

One **Coordinator Agent** receives all incoming tasks, classifies them, and delegates to the correct **Specialist Agent**.

```
                    ┌─────────────┐
User Request ──────→│  COORDINATOR│
                    │   AGENT     │
                    └──────┬──────┘
                           │ classifies & routes
          ┌────────────────┼────────────────┐
          ↓                ↓                ↓
  ┌───────────────┐ ┌─────────────┐ ┌──────────────┐
  │ BILLING AGENT │ │TECH SUPPORT │ │ RETURNS AGENT│
  │               │ │    AGENT    │ │              │
  └───────────────┘ └─────────────┘ └──────────────┘
```

Specialists work **in parallel** — independent of each other.

---

## Pattern 1 — Coordinator in Detail

<!-- _class: invert small -->

**Real-world example: Customer Support System**

```
User: "My order #4521 arrived broken and I was charged twice."

Coordinator Agent:
  CLASSIFY → Two issues detected:
             Issue 1: Damaged product → route to Returns Agent
             Issue 2: Billing error   → route to Billing Agent

Returns Agent (runs in parallel):
  → Looks up order #4521
  → Initiates replacement shipment
  → Returns: "Replacement shipped, arrives in 2 days"

Billing Agent (runs in parallel):
  → Checks payment history for customer
  → Confirms duplicate charge
  → Issues refund of $45.99
  → Returns: "Refund processed in 3-5 business days"

Coordinator Agent:
  → Combines both responses
  → Returns unified reply to user
```

**Result: Both issues resolved simultaneously. Faster than one agent handling them sequentially.**

---

## Pattern 1 — Try It Yourself

Design a Coordinator pattern for a **School Administration System**. A student sends: *"I need to enroll in Python 201, update my contact email, and get my transcript."*

1. What does the Coordinator Agent do first?
2. How many specialist agents are needed?
3. What does each specialist do?
4. Can they run in parallel? Why or why not?
5. **Challenge:** What happens if the Enrollment Agent fails (course is full)? How should the Coordinator handle it?

---

## Pattern 2 — Sequential

### What question does it answer?
*"How do I build a pipeline where each step depends on the previous one?"*

Each agent completes its task and **passes its output** to the next agent in the chain.

```
Input
  ↓
┌──────────────┐
│  AGENT 1     │  "Research the topic"
│  Researcher  │
└──────┬───────┘
       │ research notes
       ↓
┌──────────────┐
│  AGENT 2     │  "Write a draft from the notes"
│  Writer      │
└──────┬───────┘
       │ draft article
       ↓
┌──────────────┐
│  AGENT 3     │  "Edit and polish the draft"
│  Editor      │
└──────┬───────┘
       │ final article
       ↓
    Output
```

---

## Pattern 2 — Sequential in Detail

<!-- _class: invert small -->

**Real-world example: Content Marketing Pipeline**

```
Step 1 — Research Agent:
  Input:  "Write about AI in education"
  Action: Search web, read 5 articles, extract key points
  Output: Research notes (bullet points, stats, quotes)

Step 2 — Writer Agent:
  Input:  Research notes from Step 1
  Action: Draft a 800-word article using the notes
  Output: Draft article (structured, with headings)

Step 3 — SEO Agent:
  Input:  Draft article from Step 2
  Action: Optimize keywords, add meta description, check readability
  Output: SEO-optimized article

Step 4 — Editor Agent:
  Input:  SEO article from Step 3
  Action: Fix grammar, improve flow, ensure brand voice
  Output: Final published-ready article
```

**Key rule:** Each agent only receives what it needs. The Writer doesn't need to know how to search. The Editor doesn't need to know SEO. Clean separation of concerns.

---

## Pattern 2 — Try It Yourself

Design a Sequential pipeline for **processing a student's Python assignment**:

1. List all the agents needed (minimum 3)
2. Define what each agent receives as input
3. Define what each agent produces as output
4. Why must these agents run in sequence and not in parallel?

**Challenge:** A teacher wants to add a **plagiarism check** to this pipeline. Where in the sequence does it go? What does it receive and what does it output?

---

## Pattern 3 — Iterative Refinement

### What question does it answer?
*"How do I improve quality through multiple review cycles?"*

Two agents — a **Generator** and a **Critic** — loop until the output meets quality standards.

```
Input (goal + quality criteria)
  ↓
┌──────────────┐
│  GENERATOR   │ ←─────────────────────────┐
│    AGENT     │                           │
└──────┬───────┘                           │
       │ first draft                       │ revised draft
       ↓                                   │
┌──────────────┐                           │
│   CRITIC     │                           │
│    AGENT     │ ──── "needs improvement" ─┘
└──────┬───────┘
       │
       │ "quality threshold met"
       ↓
    Final Output
```

---

## Pattern 3 — Iterative Refinement in Detail

<!-- _class: invert small -->

**Real-world example: Code Review System**

```
Iteration 1:
  Generator: Write authentication module for Flask app
  Output:    auth.py — basic implementation, 87 lines

  Critic:    Review auth.py for security, style, and correctness
  Feedback:  "Missing rate limiting. JWT secret hardcoded. No input validation."
  Decision:  Below quality threshold → loop again

Iteration 2:
  Generator: Revise auth.py based on critic feedback
  Output:    auth.py — improved, 124 lines, rate limiting added

  Critic:    Review revised auth.py
  Feedback:  "Rate limiting ✓. JWT now uses env var ✓. Still missing logout."
  Decision:  Partial — loop again

Iteration 3:
  Generator: Add logout endpoint, finalize
  Critic:    All criteria met ✓ — security ✓ style ✓ correctness ✓
  Decision:  Quality threshold met → STOP
```

**Result: 3 iterations produced production-quality code. Generator alone would have produced iteration 1 quality.**

---

## Pattern 3 — Try It Yourself

1. Why can't the Generator evaluate its own output effectively?

2. Design a Critic Agent for **student essay grading**. What quality criteria should it check? What feedback format should it give the Generator Agent?

3. **Think about it:** How do you prevent an infinite loop in Iterative Refinement? What conditions should trigger the STOP decision even if quality isn't perfect?

4. **Challenge:** Design an Iterative Refinement system for **generating SQL queries**. The Generator writes queries; the Critic checks correctness, performance, and safety. What does the Critic specifically look for?

---

## Pattern 4 — Human-in-the-Loop

### What question does it answer?
*"How do I keep a human in control for high-risk decisions?"*

The agent **pauses at critical points** and waits for human approval before continuing.

```
Agent working autonomously...
         ↓
  ┌─────────────────────────┐
  │ DECISION POINT REACHED  │
  │ (high risk action)      │
  └──────────┬──────────────┘
             │ pause + notify human
             ↓
    ┌─────────────────┐
    │   HUMAN REVIEW  │
    │                 │
    │ Approve / Reject│
    │ Modify / Escalate│
    └────────┬────────┘
             │
    ┌────────┴────────┐
    │                 │
  APPROVE           REJECT
    │                 │
  Continue         Stop or
  autonomously     revise
```

---

## Pattern 4 — Human-in-the-Loop in Detail

<!-- _class: invert small -->

**Real-world example: Automated Refund Processing**

```
Step 1 (Autonomous):
  Agent reads refund request: customer #C881, order #5512, $340 refund claim
  Agent checks: order exists ✓ product returned ✓ within policy window ✓

Step 2 (Autonomous):
  Refund amount: $340
  Company policy: auto-approve refunds ≤ $200
  Decision: $340 > $200 threshold → PAUSE

Step 3 (Human-in-the-Loop):
  Agent sends notification to manager:
  "Refund request $340 for order #5512. Reason: damaged product.
   Policy verified. Awaiting your approval."

Step 4 (Human decides):
  Manager reviews → APPROVES

Step 5 (Autonomous resumes):
  Agent processes $340 refund
  Sends confirmation email to customer
  Updates CRM
```

**The agent handles 90% of the work. The human only reviews the 10% that matters.**

---

## Pattern 4 — Try It Yourself

1. You are building a student grade modification system. The agent can update grades automatically. When should it PAUSE and require a teacher's approval?
   - Correcting a typo (85 → 85.0)
   - Changing a failing grade to passing
   - Adjusting one question's mark
   - Deleting a grade entirely

2. **Design the pause notification** the agent sends to the teacher. What information must it include for the teacher to make a good decision?

3. **Challenge:** What happens if the human never responds? Design the timeout behavior for this agent — what should it do after 24 hours with no response?

---

## Pattern Selection Matrix

<!-- _class: invert small -->

Use this to choose the right pattern for your problem:

| If your problem has... | Use this pattern | Why |
|------------------------|-----------------|-----|
| Different request types needing different expertise | **Coordinator** | Route to the right specialist |
| Steps that depend on each other in order | **Sequential** | Each step builds on the previous |
| Quality-critical output that needs multiple passes | **Iterative Refinement** | Generator + Critic loop improves quality |
| High-risk actions requiring human judgment | **Human-in-the-Loop** | Keeps humans in control where it matters |
| Independent subtasks that can run at the same time | **Coordinator** | Parallel execution saves time |
| Creative or subjective output (writing, design) | **Iterative Refinement** | Subjective quality benefits from critique cycles |

---

## Combining Patterns

<!-- _class: invert small -->

Real systems use multiple patterns together:

**Example: Legal Contract Review System**

```
Step 1 — COORDINATOR:
  Receives contract → routes sections to specialists:
    → Financial Terms Agent
    → Liability Clauses Agent
    → Compliance Agent (run in parallel)

Step 2 — SEQUENTIAL:
  Each specialist's report feeds into a Summary Agent
  Summary Agent creates unified risk report

Step 3 — ITERATIVE REFINEMENT:
  Generator Agent writes the final recommendation
  Critic Agent checks legal accuracy and completeness
  Loop until quality threshold met

Step 4 — HUMAN-IN-THE-LOOP:
  Final recommendation sent to lawyer for approval
  Lawyer approves/modifies before client delivery
```

**This is a Level 3 agent (Multi-Agent) using all 4 patterns.**

---

## How Claude Code Uses These Patterns

Claude Code — the tool you use every day — uses all 4 patterns internally:

| Pattern | How Claude Code Uses It |
|---------|------------------------|
| **Coordinator** | Routes your request to the right sub-agent (file reader, code runner, searcher) |
| **Sequential** | Reads file → understands error → writes fix → runs tests — in sequence |
| **Iterative Refinement** | Runs tests, sees failures, revises code, runs again — loops until tests pass |
| **Human-in-the-Loop** | Pauses and asks you before deleting files or making large changes |

> **You have been using multi-agent patterns every time you've used Claude Code.**

---

## Common Mistakes

<!-- _class: invert small -->

| Mistake | Wrong Thinking | Reality |
|---------|---------------|---------|
| "Use Coordinator for everything" | Routing is always the answer | Some problems need sequential order, not parallel routing |
| "More agents = better quality" | More specialists = smarter system | More agents = more complexity + more failure points |
| "Skip Human-in-the-Loop to save time" | Automation should be full | High-risk decisions need humans — legal, financial, medical |
| "Iterative Refinement will loop forever" | It keeps improving until perfect | Always set a max iteration count and a minimum quality threshold |
| "Sequential is just a queue" | Order doesn't matter | Each agent in sequence uses the previous agent's output — order is critical |
| "Patterns are mutually exclusive" | Pick one and stick to it | Production systems combine multiple patterns |

---

## Quick Reference Card

```
4 MULTI-AGENT DESIGN PATTERNS

1. COORDINATOR
   One agent routes → specialists work in parallel
   Use when: Different request types, independent subtasks

2. SEQUENTIAL
   Agent 1 output → Agent 2 input → Agent 3 input → ...
   Use when: Each step depends on the previous

3. ITERATIVE REFINEMENT
   Generator → Critic → loop until quality met
   Use when: Quality-critical, subjective, or complex output

4. HUMAN-IN-THE-LOOP
   Agent works → PAUSE at risk point → human approves → resume
   Use when: High-risk decisions, legal/financial/medical actions

COMBINING: Real systems use multiple patterns together
CLAUDE CODE uses all 4 patterns internally
```

---

## What's Next — Agent Ops

You now know how agents work and how they collaborate.

**Next (61.5):** How do you know if your agent is *working well* in production?

Agent Ops covers:
- **LM-as-Judge** — using an AI to evaluate AI output
- **Golden Datasets** — your agent's test suite
- **Traces** — complete records of every agent step
- **Human Feedback Loops** — improving agents over time

**Preparation question:**
*A customer support agent resolves 80% of tickets. Is that good or bad? How would you know? What would you measure?*
