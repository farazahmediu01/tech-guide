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

# Chapter 61.2 — Core Agent Architecture
## Student Learning Guide
**Source:** Agent Factory — Panaversity
**URL:** agentfactory.panaversity.org/docs/Building-Agent-Factories/introduction-to-ai-agents

---

## What You Will Learn

By the end of this guide you will be able to:

- Name and explain all 4 components of the 3+1 Architecture Framework
- Describe what each component does and why removing any one breaks the agent
- Trace a real task through all 4 components step by step
- Identify which component is responsible when an agent fails
- Explain the two types of memory an agent can have
- Name the three reasoning strategies: ReAct, Chain-of-Thought, and Reflection

> **Why this matters:** This framework applies to EVERY agent you will ever build — regardless of which SDK, language, or cloud you use.

---

## The 3+1 Architecture Framework

Every AI agent — no matter how simple or complex — is built from exactly 4 components.

```
┌─────────────────────────────────────────────────────┐
│                   AI AGENT                          │
│                                                     │
│   ┌──────────┐    ┌──────────┐    ┌─────────────┐  │
│   │  MODEL   │    │  TOOLS   │    │ORCHESTRATION│  │
│   │          │    │          │    │             │  │
│   │ The Brain│    │ The Hands│    │ The Nervous │  │
│   │          │    │          │    │   System    │  │
│   └──────────┘    └──────────┘    └─────────────┘  │
│                                                     │
│   ┌─────────────────────────────────────────────┐  │
│   │              DEPLOYMENT                     │  │
│   │                The Body                     │  │
│   └─────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

The first 3 make the agent work. The +1 (Deployment) makes it accessible.

---

## Component 1 — The Model (The Brain)

### What question does it answer?
*"What does the agent think, reason, and decide with?"*

The Model is the language model at the core of the agent. It provides:
- **Reasoning** — understanding the task, planning steps
- **Language understanding** — reading tool outputs, user inputs
- **Decision making** — choosing which tool to call, when to stop

```
Examples of models used as agent brains:
  Claude 3.5 Sonnet    → complex reasoning, coding tasks
  Claude 3 Haiku       → fast, cheap, high-volume tasks
  GPT-4o               → broad capability, tool use
  Gemini 1.5 Pro       → long context, multimodal tasks
```

> **The model does NOT act on its own.** It reasons about what to do — the orchestration component executes the plan.

---

## Component 1 — Try It Yourself

1. Why can't you build an agent without a model?

2. If you need an agent that handles 10,000 customer queries per day at low cost, which model characteristic matters most? Speed? Intelligence? Cost?

3. **Think about it:** The same agent can use different models. A customer support agent might use Haiku for simple FAQs and switch to Sonnet for complex complaints. What does this tell you about the relationship between the model and the rest of the agent?

4. **Challenge:** What would happen if you replaced the language model in an agent with a rule-based system (like a bunch of `if/else` statements)? Would it still be an agent? Why or why not?

---

## Component 2 — Tools (The Hands)

### What question does it answer?
*"What actions can the agent actually take in the world?"*

Without tools, an agent can only think. Tools are what allow it to **act**.

```
Common Agent Tools:

  read_file(path)              → Read a file from disk
  write_file(path, content)    → Write or modify a file
  run_code(code)               → Execute Python/shell code
  web_search(query)            → Search the internet
  call_api(url, params)        → Call an external API
  query_database(sql)          → Run a SQL query
  send_email(to, subject, body)→ Send an email
  create_ticket(details)       → Create a support ticket
```

Every tool has: **defined inputs**, **defined outputs**, and **permission boundaries**.

---

## Tools — Permission Boundaries

<!-- _class: small -->

This is critical for production agents. Every tool must define what it is **allowed** to do.

| Tool | Allowed | NOT Allowed |
|------|---------|-------------|
| `read_file` | Read any file in `/workspace/` | Read `/etc/passwd` or system files |
| `send_email` | Send to customers in the CRM | Send to arbitrary external addresses |
| `process_refund` | Approve refunds up to $200 | Approve refunds above $200 |
| `query_database` | SELECT queries on `products` table | DROP TABLE, DELETE, UPDATE |
| `web_search` | Search approved domains | Access internal company URLs |

> **Rule:** Give an agent the minimum tools it needs. Every extra tool is an extra attack surface.

This is called the **Principle of Least Privilege** — more on this in the Security chapter.

---

## Component 2 — Try It Yourself

Design the tool list for these agents. For each tool, specify what it is allowed and NOT allowed to do:

1. **Student Assignment Grader Agent**
   - Reads student Python files
   - Runs the code and checks output
   - Returns a grade and feedback

2. **Customer Support Agent for an e-commerce store**
   - Answers questions about orders
   - Can issue refunds
   - Can escalate to a human

3. **Challenge:** A student asks: *"Can I give my agent access to the entire file system?"* What do you tell them and why?

---

## Component 3 — Orchestration (The Nervous System)

### What question does it answer?
*"How does the agent decide what to do next and remember what happened?"*

Orchestration is the most complex component. It has three parts:

```
ORCHESTRATION
├── Planning         → Breaking the goal into steps
├── Memory           → Remembering what happened
│   ├── Short-term   → Current conversation / task context
│   └── Long-term    → Persisted knowledge across sessions
└── Reasoning Strategy
    ├── ReAct              → Reason + Act interleaved
    ├── Chain-of-Thought   → Think step by step before acting
    └── Reflection         → Review and improve own output
```

---

## Orchestration — Memory

<!-- _class: small -->

An agent without memory is like a person with amnesia. Every task starts from zero.

**Short-Term Memory**
- Exists only during the current task or conversation
- Contains: the current goal, tool results so far, reasoning steps taken
- Think of it as the agent's **working memory** — like your RAM
- Automatically cleared when the session ends

**Long-Term Memory**
- Persists across sessions — stored in a database or vector store
- Contains: user preferences, past interactions, learned facts
- Think of it as the agent's **knowledge base** — like a hard drive
- Examples: "This user prefers formal tone", "Last support ticket was about billing"

**Why it matters for web apps:**
A customer support agent with long-term memory knows a customer's history.
Without it, every conversation starts from scratch — frustrating for users.

---

## Orchestration — Reasoning Strategies

<!-- _class: small -->

The orchestration layer can use different strategies to improve output quality.

**ReAct (Reason + Act)**
The most common strategy. The agent alternates between reasoning and acting.
```
Think: "I need to find the bug. I should read the error first."
Act:   read_file("error_log.txt")
Think: "The error is on line 42 in auth.py. I should look at that."
Act:   read_file("auth.py", line=42)
Think: "Found it. Missing null check. I'll fix it."
Act:   edit_file("auth.py", fix)
```

**Chain-of-Thought**
The agent writes out its full reasoning before acting.
```
"First I will... then I will... because... therefore my first step is..."
```

**Reflection**
The agent reviews and critiques its own output before delivering it.
```
"My answer was: [X]. But wait — did I consider edge case Y? Let me revise..."
```

---

## Component 3 — Try It Yourself

1. An agent is helping a student debug their code. It has fixed 3 bugs in this session. The student closes the chat and opens a new one. What does the agent remember? (Short-term vs long-term memory)

2. Which reasoning strategy is best for each scenario:
   - Writing a formal business report (quality matters most)
   - Answering simple FAQ questions quickly
   - Debugging a complex multi-file codebase

3. **Think about it:** A customer support agent remembers that a user complained about a billing issue 3 months ago. The user calls again. How does long-term memory change the interaction?

4. **Challenge:** Design the memory system for a Personal Study Assistant agent for Aptech students. What goes in short-term? What goes in long-term?

---

## Component 4 — Deployment (The Body)

### What question does it answer?
*"How does the agent become accessible to users and other systems?"*

An agent that runs on your laptop and can't be reached by anyone is useless in production. Deployment is what makes it real.

```
Deployment options:

  API Endpoint      → Agent exposed as a REST API
                      Other apps call it via HTTP

  Chat Interface    → Agent embedded in a web/mobile UI
                      Users talk to it directly

  Background Worker → Agent runs on a schedule or trigger
                      No direct user interaction needed

  CLI Tool          → Agent runs in the terminal
                      Developer-facing workflows

  Webhook           → Agent triggered by external events
                      (new order, new email, new ticket)
```

---

## Deployment — Why It's the "+1"

<!-- _class: small -->

The first 3 components (Model, Tools, Orchestration) define what the agent **can do**.

Deployment defines **who can access it and how**.

| Deployment Type | Who uses it | Example |
|----------------|-------------|---------|
| **API Endpoint** | Other software systems | A billing agent called by your web app |
| **Chat Interface** | End users directly | A support chatbot on your website |
| **Background Worker** | No one — runs automatically | An agent that monitors logs every hour |
| **CLI Tool** | Developers | Claude Code running in your terminal |
| **Webhook** | Triggered by events | An agent that processes new emails |

> The same agent can have multiple deployment types. A customer support agent might have a chat interface AND an API endpoint for integration with your CRM.

---

## Component 4 — Try It Yourself

For each agent below, choose the best deployment type and explain why:

1. An agent that grades student Python assignments when submitted
2. An agent that answers student questions in real time during class
3. An agent that monitors your database every 30 minutes for unusual activity
4. An agent that other developers can call from their code to validate SQL queries
5. **Challenge:** Design the deployment for a "Teaching Assistant Agent" for Aptech students. Where does it live? How do students access it? When does it run?

---

## Full Workflow — All 4 Components Together

**Task:** *"Fix the failing test in auth.py"* (given to Claude Code)

```
DEPLOYMENT  → Claude Code receives the task via terminal (CLI deployment)
              Passes it to the orchestration layer

ORCHESTRATION → Plans: "I need to read the file, find the test,
                run it, understand the error, fix the code, verify"
                Activates short-term memory for this task

MODEL       → Reasons: "First I should read the failing test"
              Decides: "Call read_file tool"

TOOLS       → read_file("auth.py") executes
              Returns: file contents to orchestration

ORCHESTRATION → Updates memory with file content
MODEL       → Reasons: "Now I need to run the test"
TOOLS       → run_pytest("auth.py") executes → error output returned

MODEL       → Reasons: "Error is missing null check on line 42"
              Decides: "Call edit_file tool"
TOOLS       → edit_file("auth.py", fix) executes

MODEL       → Reasons: "Verify the fix"
TOOLS       → run_pytest("auth.py") → all tests pass

DEPLOYMENT  → Returns result to the user in terminal
```

---

## The Debugging Framework

<!-- _class: small -->

When an agent fails, this framework tells you WHICH component to fix.

| Symptom | Which Component | What to Check |
|---------|----------------|---------------|
| Agent gives wrong or irrelevant answers | **Model** | Is the model capable enough? Is the prompt clear? |
| Agent tries to call tools but they fail | **Tools** | Are tools correctly defined? Are permissions right? |
| Agent loses track of the task halfway | **Orchestration / Memory** | Is context window too small? Is memory being saved? |
| Agent works locally but users can't reach it | **Deployment** | Is the endpoint live? Is authentication working? |
| Agent does too much / too little autonomy | **Orchestration** | Review the reasoning strategy and planning rules |

> **Production tip:** Always log which component failed. This saves hours of debugging.

---

## Common Mistakes

<!-- _class: small -->

| Mistake | Wrong Thinking | Reality |
|---------|---------------|---------|
| "The model IS the agent" | Just swap the LLM to fix everything | The model is only 1 of 4 components |
| "More tools = better agent" | Give the agent every possible tool | More tools = more attack surface + more confusion |
| "Deployment is just a detail" | Build the agent, worry about deployment later | Deployment defines who uses it — design it early |
| "Short-term memory is enough" | Users don't need continuity | Without long-term memory, every session starts from zero |
| "Chain-of-Thought is always best" | Slower thinking = better results | ReAct is faster for simple tasks; CoT for complex ones |
| "Orchestration happens automatically" | SDKs handle all of this | You must explicitly configure memory, planning, and reasoning strategy |

---

## Quick Reference Card

```
THE 3+1 ARCHITECTURE FRAMEWORK

┌─────────────────────────────────────────────────┐
│ COMPONENT       │ ROLE         │ KEY QUESTION    │
├─────────────────┼──────────────┼─────────────────┤
│ Model           │ The Brain    │ What to do?     │
│ Tools           │ The Hands    │ How to act?     │
│ Orchestration   │ Nervous Sys. │ Plan + Remember │
│ Deployment (+1) │ The Body     │ Who can use it? │
└─────────────────┴──────────────┴─────────────────┘

ORCHESTRATION SUB-COMPONENTS:
  Planning    → Break goal into steps
  Memory      → Short-term (session) + Long-term (persisted)
  Reasoning   → ReAct | Chain-of-Thought | Reflection

DEBUGGING:
  Wrong answers   → Model
  Tool failures   → Tools
  Lost context    → Orchestration/Memory
  Can't connect   → Deployment
```

---

## What's Next — The Agentic Problem-Solving Process

You now know what's inside an agent.

**Next (61.3):** You will learn how an agent *thinks through a problem* — the structured process it follows from receiving a goal to delivering a result.

This is the 5-Step Loop:
```
Step 1: Receive Goal
Step 2: Plan
Step 3: Act (tool calls)
Step 4: Observe & Update
Step 5: Evaluate — done or loop again?
```

**Preparation question:**
*An agent is asked: "Write a research report on the impact of AI on education."*
*Without knowing the 5-step loop yet — what steps do you think it should take? Write them down.*
