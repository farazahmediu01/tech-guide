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

# Chapter 61.5 — Agent Ops
## Student Learning Guide
**Source:** Agent Factory — Panaversity
**URL:** agentfactory.panaversity.org/docs/Building-Agent-Factories/introduction-to-ai-agents

---

## What You Will Learn

By the end of this guide you will be able to:

- Explain why traditional software testing fails for agents
- Use LM-as-Judge to evaluate agent output quality
- Design a Golden Dataset for any agent you build
- Read and interpret agent traces to debug problems
- Set up Human Feedback Loops for continuous improvement
- Define KPIs (Key Performance Indicators) for a production agent

> **Why this matters:** Building an agent is 30% of the work. Running it reliably in production is 70%. Agent Ops is what separates a demo from a Digital FTE you can sell.

---

## The Core Challenge — Why Testing Agents Is Hard

Testing a traditional program is simple:

```python
# Traditional software test — deterministic
def test_add():
    assert add(2, 3) == 5  # Always exactly 5. Pass or fail.
```

Testing an agent is completely different:

```
Task: "Summarize this customer complaint professionally"

Valid response A: "The customer reports a delayed delivery and requests
                  a status update. Recommend proactive communication."

Valid response B: "Order delay complaint. Customer seeks ETA.
                  Priority: medium. Action: send tracking update."

Valid response C: "Customer is frustrated about late shipment.
                  Suggest immediate follow-up with tracking info."
```

**All three are correct. All three are different.** Traditional `assert` testing breaks here.

---

## The Mindset Shift

This is the most important concept in Agent Ops:

```
Traditional Testing Mindset:
  "Is my agent CORRECT?"
  → Binary: pass / fail
  → Fixed expected output
  → Works for deterministic software

Agent Ops Mindset:
  "Is my agent IMPROVING toward its KPIs?"
  → Spectrum: 0–10 quality score
  → Multiple valid outputs
  → Works for probabilistic, language-based systems
```

> You are not asking "did it give the right answer?"
> You are asking "is this answer good enough, and is it getting better?"

---

## The 4 Pillars of Agent Ops

```
┌─────────────────────────────────────────────────┐
│                  AGENT OPS                      │
│                                                 │
│  Pillar 1: LM-as-Judge                          │
│  "Use AI to evaluate AI"                        │
│                                                 │
│  Pillar 2: Golden Datasets                      │
│  "Your agent's test suite"                      │
│                                                 │
│  Pillar 3: Traces                               │
│  "Complete record of every step"                │
│                                                 │
│  Pillar 4: Human Feedback Loops                 │
│  "Real users improve the agent over time"       │
└─────────────────────────────────────────────────┘
```

---

## Pillar 1 — LM-as-Judge

### What question does it answer?
*"Is this agent output good quality — and by how much?"*

You use a **separate language model** (the Judge) to evaluate the output of your agent against a quality rubric.

```
Your Agent produces:
  "The customer is upset about a billing error. They want a refund."

LM-as-Judge evaluates using rubric:
  Criterion 1: Professional tone?     → Score: 7/10 (slightly informal)
  Criterion 2: Key facts captured?    → Score: 10/10 (billing error + refund)
  Criterion 3: Actionable?            → Score: 4/10 (no recommended action)
  Criterion 4: Appropriate length?    → Score: 8/10 (concise but complete)

  Overall Score: 7.25 / 10
  Feedback: "Add a recommended action (e.g., initiate refund review)"
```

---

## LM-as-Judge — Scoring Rubric

<!-- _class: small -->

The Agent Factory uses a 4-level scoring scale:

| Score | Label | Meaning |
|-------|-------|---------|
| **10** | Excellent | Fully meets all criteria, production-ready |
| **7** | Good | Meets most criteria, minor improvements needed |
| **4** | Partial | Meets some criteria, significant gaps |
| **0** | Fail | Does not meet criteria, fundamentally wrong |

**Why these 4 levels, not 1–10?**

Because humans (and models) can reliably distinguish 4 levels.
Asking "is this a 6 or a 7?" produces inconsistent judgments.
Asking "is this Excellent, Good, Partial, or Fail?" produces consistent ones.

---

## LM-as-Judge — Try It Yourself

Below is a student agent's response to: *"Explain what a Python list is to a beginner."*

```
"A list is a data structure. Lists use square brackets.
You can add items. Lists are mutable."
```

**Using the 4-level rubric, score this response on:**

1. **Accuracy** — Is the information correct?
2. **Clarity** — Is it understandable for a beginner?
3. **Examples** — Does it include a code example?
4. **Completeness** — Does it cover the key concepts?

**Write the specific feedback** the Judge would give to help the agent improve its next response.

---

## Pillar 2 — Golden Datasets

### What question does it answer?
*"How do I systematically test my agent across many realistic scenarios?"*

A **Golden Dataset** is a curated collection of test cases — real inputs paired with expected quality criteria.

```
Golden Dataset Entry #1:
  Input:    "I was charged twice for order #5512"
  Expected: Agent should:
            ✓ Identify it as a billing complaint
            ✓ Reference the specific order number
            ✓ Offer a clear next step (refund review or investigation)
            ✓ Maintain professional and empathetic tone
            ✗ Should NOT ask the customer for info already provided
            ✗ Should NOT promise a refund amount without verification

Golden Dataset Entry #2:
  Input:    "When will my order arrive?"
  Expected: Agent should:
            ✓ Ask for order number if not provided
            ✓ OR look up order if number is in context
            ✓ Give a specific ETA or explain why it's unknown
```

---

## Golden Dataset — Size Guidelines

<!-- _class: small -->

| Stage | Dataset Size | Purpose |
|-------|-------------|---------|
| **Development** | 20–50 cases | Catch obvious failures during building |
| **Pre-launch** | 50–100 cases | Validate agent is ready for real users |
| **Production** | 100+ cases | Catch regressions after every update |
| **Enterprise** | 200+ cases | Required for high-stakes deployments (97%+ pass rate) |

**What makes a good Golden Dataset?**

```
✓ Covers common cases (80% of real requests)
✓ Covers edge cases (unusual but valid requests)
✓ Covers adversarial cases (confusing, ambiguous, or hostile inputs)
✓ Reflects real user language (not perfect grammar, abbreviations, typos)
✓ Updated regularly as new failure patterns emerge from production
```

> **Enterprise rule:** A 97%+ pass rate on your Golden Dataset is the minimum threshold before deploying an agent to paying customers.

---

## Pillar 2 — Try It Yourself

You are building a **Student Assignment Helper Agent** for Aptech. It helps students understand their assignment errors.

**Design 5 Golden Dataset entries:**

For each entry, write:
1. The student's input message
2. What the agent MUST do (at least 3 criteria)
3. What the agent must NOT do (at least 1 constraint)

**Include at least:**
- 1 common case (student has a syntax error)
- 1 edge case (student submits correct code but asks why it's wrong)
- 1 adversarial case (student asks the agent to "just give me the answer")

---

## Pillar 3 — Traces

### What question does it answer?
*"Exactly what did my agent do, step by step, and where did it go wrong?"*

A **Trace** is a complete, timestamped record of every step the agent took during a task.

```
TRACE: Session ID 7f3a9b | 2026-03-30 14:23:01

[14:23:01] GOAL RECEIVED
  Input: "Process refund for order #5512"

[14:23:02] REASONING
  "Need to verify order exists and check refund eligibility"

[14:23:03] TOOL CALL: query_database
  SQL: SELECT * FROM orders WHERE id = 5512
  Result: Order found. Amount: $340. Status: delivered. Date: 2026-03-01.

[14:23:04] REASONING
  "Order confirmed. $340 exceeds $200 auto-approve limit."

[14:23:05] ACTION: pause_for_human_approval
  Notification sent to: manager@store.com
  Waiting...

[14:23:47] HUMAN RESPONSE: APPROVED

[14:23:48] TOOL CALL: process_refund
  Amount: $340, Customer: C881
  Result: Refund initiated. Reference: REF-9921

[14:23:49] TASK COMPLETE
  Duration: 48 seconds | Tools called: 2 | Human approvals: 1
```

---

## Reading a Trace to Debug

<!-- _class: small -->

When your agent fails, the trace tells you exactly where and why.

**Trace showing a failure:**

```
[14:30:01] GOAL RECEIVED: "Summarize complaints from last week"

[14:30:02] TOOL CALL: query_database
  SQL: SELECT * FROM complaints WHERE date >= '2026-03-23'
  Result: ERROR — column "date" does not exist

[14:30:03] REASONING
  "Query failed. I'll try 'created_at' instead"

[14:30:04] TOOL CALL: query_database
  SQL: SELECT * FROM complaints WHERE created_at >= '2026-03-23'
  Result: 0 rows returned

[14:30:05] TASK FAILED
  Reason: No data found matching criteria
```

**What the trace tells you:**
- Line 2: Wrong column name (`date` vs `created_at`) → fix the tool schema
- Line 4: Correct column but no results → date range may be wrong
- The agent tried to recover — good. But the second query was still wrong.

---

## Pillar 3 — Try It Yourself

Read this trace and answer the questions:

```
[09:15:01] GOAL: "Send weekly report to all teachers"
[09:15:02] TOOL CALL: query_database → "SELECT email FROM teachers"
           Result: 12 emails returned
[09:15:03] TOOL CALL: send_email → to: teacher1@school.com ✓
[09:15:04] TOOL CALL: send_email → to: teacher2@school.com ✓
[09:15:05] TOOL CALL: send_email → to: teacher3@school.com
           Result: ERROR — rate limit exceeded
[09:15:05] TASK FAILED
```

1. At what step did the agent fail?
2. What caused the failure?
3. How should the agent have handled this differently?
4. **Challenge:** Redesign the agent's email-sending logic to handle rate limits gracefully.

---

## Pillar 4 — Human Feedback Loops

### What question does it answer?
*"How do I use real user feedback to continuously improve my agent?"*

You collect structured feedback from actual users and feed it back into agent improvement.

```
Feedback Collection Methods:

  👍/👎 Button       → Simple signal: was this response helpful?
  1–5 Star Rating    → More granular satisfaction signal
  Free-text comment  → "This response missed my actual question"
  Escalation signal  → User asked for a human = implicit negative
  Resolution signal  → Did the issue get resolved? = implicit positive
```

**What you do with the feedback:**
1. Negative feedback → add to Golden Dataset → find root cause via traces → improve prompt or tools
2. Positive feedback → identify what worked → reinforce in agent design
3. Escalation patterns → reveal gaps in agent capability → add new tools or skills

---

## KPIs — Measuring Agent Performance

<!-- _class: small -->

Define these **before** you deploy. If you don't know what success looks like, you can't improve.

**Example KPIs for a Customer Support Agent:**

| KPI | Target | How Measured |
|-----|--------|-------------|
| First Response Time | < 30 seconds | Trace timestamps |
| Resolution Rate | > 80% without escalation | Escalation logs |
| User Satisfaction | > 4.2 / 5 stars | Post-chat rating |
| Correct Classification | > 95% | LM-as-Judge vs Golden Dataset |
| Escalation Rate | < 10% | Human handoff logs |
| Cost per Resolved Ticket | < $0.15 | Token usage logs |

**Review these weekly.** If a KPI drops — open traces, find the failure pattern, fix it.

---

## Putting It All Together — The Agent Ops Cycle

```
BUILD AGENT
     ↓
Create Golden Dataset (20-50 cases)
     ↓
Run agent against dataset
     ↓
LM-as-Judge scores each output
     ↓
Pass rate ≥ 97%? ──── NO ──→ Fix agent (prompt, tools, memory)
     │                              ↑
    YES                             │
     ↓                    Review traces to find root cause
DEPLOY TO PRODUCTION
     ↓
Collect Human Feedback
     ↓
Monitor KPIs weekly
     ↓
Failure detected? ─── YES ──→ Add to Golden Dataset
     │                               ↑
    NO                               └── Fix → re-test → re-deploy
     ↓
CONTINUOUSLY IMPROVING AGENT
```

---

## Common Mistakes

<!-- _class: small -->

| Mistake | Wrong Thinking | Reality |
|---------|---------------|---------|
| "My agent passed my tests" | Unit tests = production ready | Agent tests use probabilistic scoring, not binary pass/fail |
| "Golden Dataset is a one-time task" | Build it once and forget it | Update it every time a new failure pattern emerges |
| "Traces are just logs" | Logs and traces are the same | Traces capture reasoning + tool calls + timing — far richer than logs |
| "User feedback is optional" | The agent's performance speaks for itself | Human feedback reveals gaps that automated evaluation misses |
| "No KPIs means no constraints" | Freedom = better agent | No KPIs = no direction = no improvement |
| "High resolution rate = success" | 80% resolution = great | 80% resolution with 1-star satisfaction ratings = failing |

---

## Quick Reference Card

```
AGENT OPS — 4 PILLARS

1. LM-AS-JUDGE
   Use AI to score AI output on a rubric
   Scoring: 10 (excellent) | 7 (good) | 4 (partial) | 0 (fail)

2. GOLDEN DATASET
   Curated test cases with expected criteria
   Sizes: 20-50 (dev) | 100+ (production) | 200+ (enterprise)
   Target: 97%+ pass rate before launch

3. TRACES
   Complete timestamped record of every agent step
   Contains: reasoning, tool calls, results, timing, errors
   Use to: debug failures, find root causes, optimize performance

4. HUMAN FEEDBACK LOOPS
   👍/👎, ratings, free text, escalation signals
   Use to: update Golden Dataset, find gaps, improve agent

THE MINDSET SHIFT:
  NOT "Is my agent correct?"
  YES "Is my agent improving toward its KPIs?"
```

---

## What's Next — Agent Interoperability & Security

You now know how to evaluate and improve agents in production.

**Next (61.6):** How do agents communicate with each other, and how do you keep them secure?

Topics:
- **A2A Protocol** — how agents talk to agents
- **Agent Cards** — an agent's identity document
- **Defense in Depth** — two layers of security every agent needs
- **Least Privilege** — giving agents only what they need

**Preparation question:**
*If you built a Billing Agent and a Refund Agent, and they need to communicate — what information would the Billing Agent need to send to the Refund Agent? How would it know what the Refund Agent can do?*
