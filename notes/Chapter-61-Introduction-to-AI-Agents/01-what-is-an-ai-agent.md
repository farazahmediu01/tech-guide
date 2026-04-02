---
marp: false
theme: default
class: invert
style: |
  section { font-size: 22px; }
  section.small { font-size: 18px; }
  section h2 { font-size: 1.4em; }
  section h3 { font-size: 1.1em; }
  pre { font-size: 0.85em; }
---

# Chapter 61.1 — What Is an AI Agent?
## Student Learning Guide
**Source:** Agent Factory — Panaversity
**URL:** agentfactory.panaversity.org/docs/Building-Agent-Factories/introduction-to-ai-agents

---

## Session Index & Learning Goals

<!-- _class: invert small -->

| # | Topic | You Will Be Able To |
|---|-------|---------------------|
| 1 | LLM vs AI Agent | Explain the key difference in one sentence |
| 2 | The 4-Step Loop | Trace any agent's execution step by step |
| 3 | The Loop in Python | Read and explain agent loop code |
| 4 | 5 Levels of Autonomy | Place any tool on the 0–4 scale |
| 5 | General vs Custom Agents | Choose the right agent type for any job |
| 6 | Director vs Bricklayer | Write better prompts that get better results |
| 7 | The Agent Factory Model | Explain how Digital FTEs are manufactured |

> **Why this matters:** Every agent you will ever build starts here. If you misunderstand what an agent *is*, you will build the wrong thing.

---

## The One-Line Definition

> **An AI agent is a system that uses a language model in a loop to reason, act, observe, and repeat — until a goal is achieved.**

Let that sink in. The key word is **loop**.

A regular LLM (ChatGPT, Claude) takes your input and gives one response. Done.

An AI agent takes your goal, reasons about what to do, takes an action, observes the result, and then reasons again — repeating until the task is complete.

---

## Regular LLM vs AI Agent


| Dimension | Regular LLM | AI Agent |
|-----------|-------------|----------|
| **How it works** | Input → Output (once) | Input → Reason → Act → Observe → Repeat |
| **Goal** | Answer a question | Complete a task |
| **Memory** | Within one conversation | Can persist across sessions |
| **Tools** | None | Can use tools (search, code, files, APIs) |
| **Autonomy** | Zero — you drive | Variable — agent drives |
| **Example** | "Explain Flask to me" | "Review my code, find bugs, fix them, run tests" |

**The loop is what makes it an agent.** Without the loop, it is just a language model.

---

## The 4-Step Agent Loop

Every agent — no matter how complex — runs this loop:

```
Step 1: REASON
        "What is the goal? What do I know? What should I do next?"

Step 2: ACT
        Execute an action — call a tool, write code, search the web,
        read a file, send a message

Step 3: OBSERVE
        Read the result of the action
        "What happened? Did it work? What changed?"

Step 4: REPEAT or STOP
        If goal not met → go back to Step 1 with new information
        If goal met → return final result to user
```

> This loop is the fundamental engine of every AI agent ever built.

---

## Real Example — The Loop in Action

**Task given to Claude Code:** *"Fix the failing test in auth.py"*

```
Loop Iteration 1:
  REASON  → "I need to see the failing test first"
  ACT     → Read auth.py
  OBSERVE → Found the test: test_login_invalid_token()

Loop Iteration 2:
  REASON  → "I need to run the test to see the error"
  ACT     → Run pytest auth.py
  OBSERVE → AssertionError: expected 401, got 200

Loop Iteration 3:
  REASON  → "The token validation is not checking expiry"
  ACT     → Edit the validate_token() function
  OBSERVE → File updated successfully

Loop Iteration 4:
  REASON  → "I should verify the fix works"
  ACT     → Run pytest auth.py again
  OBSERVE → All tests passed ✓
  STOP    → Return result to user
```

---

## The Agent Loop — In Python

<!-- _class: invert small -->

### What does the loop actually look like in code?

```python
# A simple agent loop — no SDK needed, just Python
def agent_loop(goal: str, tools: dict, max_iterations: int = 5):
    memory = []

    for i in range(max_iterations):

        # Step 1: REASON — LLM decides what to do next
        action = llm_think(goal, memory)

        # Step 4: STOP — goal is achieved
        if action["type"] == "DONE":
            return action["result"]

        # Step 2: ACT — call the right tool
        tool_fn = tools[action["tool"]]
        result = tool_fn(action["input"])

        # Step 3: OBSERVE — save what happened
        memory.append({"action": action, "result": result})

    return "Max iterations reached — task incomplete"


# Example tools the agent can use
tools = {
    "read_file":  lambda path: open(path).read(),
    "run_test":   lambda cmd: run_command(cmd),
    "edit_file":  lambda args: write_file(args["path"], args["content"]),
}

agent_loop("Fix the failing test in auth.py", tools)
```

> The loop, the memory list, and the tool dictionary — this is the skeleton of every agent you will build.

---

## The 5 Levels of Agent Autonomy


Think of this as a spectrum from "model that answers" to "system that evolves."

| Level | Name | What It Does | Example |
|-------|------|-------------|---------|
| **0** | Core Reasoning | Single response, no loop | ChatGPT answering a question |
| **1** | Tool-Augmented | Uses tools but one at a time | Claude searching the web once |
| **2** | Agentic Reasoning | Multi-step loop, plans and adapts | Claude Code fixing a bug |
| **3** | Multi-Agent | Orchestrates other agents | Triage agent routing to specialists |
| **4** | Self-Evolving | Rewrites own instructions, spawns new agents | Advanced research systems |

> **Where you are now:** You will build Level 2 and Level 3 agents.
> Level 4 is research-grade — not covered in this chapter.

---

## Try It Yourself — Levels

Look at the tools below. Place each on the 0–4 scale. Justify your answer.

1. Claude Code (fixes a bug across 10 files)
2. A chatbot that answers FAQ questions from a fixed document
3. A customer support agent that escalates to a human when confused
4. A system where one agent writes code and another agent reviews it
5. A research agent that searches, reads papers, and summarizes findings
6. A scheduling assistant that suggests meeting times from your calendar

**Discuss with a partner:** Can the same tool be at different levels depending on *how* it is used?

---

## General Agents vs Custom Agents

These are two fundamentally different types of agents.

**General Agents** (also called Foundation Agents)
- Built for anything — flexible, broad, general-purpose
- You talk to them in natural language
- Examples: Claude Code, Gemini CLI, ChatGPT
- You are the Director — they execute whatever you describe

**Custom Agents** (also called Specialist Agents or Digital FTEs)
- Built for one specific job
- Built using Agent SDKs (OpenAI Agents SDK, Google ADK, Anthropic)
- Have fixed tools, fixed workflows, fixed scope
- Can be sold as products: *"A customer support agent for $1,000/month"*

> The difference is like a **brilliant contractor** (general) vs a **trained employee** (custom).

---

## The Director vs Bricklayer Paradigm

This is one of the most important mental models in agentic AI.

| | Director Approach | Bricklayer Approach |
|-|-------------------|---------------------|
| **You say** | "Build me a login system" | "Create a file called auth.py. Now write a function called validate_token. Now add a JWT import..." |
| **Agent does** | Reasons about what to build, makes decisions, builds it | Follows your exact step-by-step instructions |
| **Your role** | Set the goal | Micromanage every step |
| **Agent autonomy** | High | Low |
| **Quality** | Often better — agent uses expertise | Limited by your knowledge |
| **When to use** | Complex tasks where agent knows more | Simple tasks or when precision is critical |

**The Agent Factory recommends the Director approach.** Trust the agent's reasoning — give it the goal, not the steps.

---

## Try It Yourself — Director vs Bricklayer

Rewrite these Bricklayer prompts as Director prompts:

1. *"Create a file. Now add a Flask import. Now write a route for /login. Now add validation..."*

2. *"Search for 'Python async'. Now open the first result. Now summarize the first paragraph..."*

3. *"Read users.py. Now find the create_user function. Now check if it validates the email..."*

**Challenge:** Write a Director prompt for this goal:
> "I want an agent that reviews student Python code submissions and gives feedback on style, correctness, and best practices."

What goal do you give it? What constraints matter? What does "done" look like?

---

## The Agent Factory Model

This is the core business insight of the Agent Factory course:

```
General Agents  →  BUILD  →  Custom Agents  →  SELL as Digital FTEs
(Claude Code)           (OpenAI SDK / ADK)      ($500–$2,000/month)
```

**How it works in practice:**

1. You use Claude Code (a General Agent) as your co-developer
2. Claude Code helps you build a Custom Agent using an Agent SDK
3. That Custom Agent is a purpose-built Digital FTE
4. You sell or deploy that Digital FTE as a product

> **You are not just learning to use AI. You are learning to manufacture AI workers.**

---

## Try It Yourself — Identifying Agents

For each scenario below, identify:
- Is it a General Agent or Custom Agent?
- What level (0–4) is it?
- Is the user acting as Director or Bricklayer?

1. A developer asks Claude Code: "Review my entire codebase and suggest improvements."
2. A business deploys a chatbot that handles refund requests up to $200.
3. A student uses ChatGPT to answer one question about Django.
4. A company builds an agent that reads invoices, extracts data, and files them automatically.
5. A researcher uses an agent that searches papers, summarizes them, and writes a literature review.

---

## Common Mistakes

| Mistake | What Students Think | The Truth |
|---------|-------------------|-----------|
| "An LLM and an agent are the same" | Both just answer questions | An agent loops — it acts, observes, and reasons repeatedly |
| "Agents are always autonomous" | Agents do everything alone | Autonomy is a spectrum (0–4). Most production agents have human oversight |
| "More autonomy = better agent" | Level 4 is always the goal | Higher autonomy = higher risk. Use the minimum autonomy needed |
| "Custom agents are smarter" | Specialized = more intelligent | Custom agents are more *reliable* for specific tasks, not smarter |
| "General agents can't be used in production" | They're just for development | General agents handle novel tasks in production all the time |
| "The loop is infinite" | Agents never stop | Agents have termination conditions — goal met, error, or max iterations reached |

---

## Quick Reference Card

```
AI AGENT = LLM + Loop (Reason → Act → Observe → Repeat)

5 LEVELS OF AUTONOMY:
  0 = Single response (no loop)
  1 = Tool-augmented (one tool call)
  2 = Agentic reasoning (multi-step loop)
  3 = Multi-agent (orchestrates other agents)
  4 = Self-evolving (rewrites own instructions)

TWO TYPES:
  General Agent  = flexible, broad, you give it any task (Claude Code)
  Custom Agent   = purpose-built, fixed scope, built with SDKs

TWO APPROACHES:
  Director   = give the goal, let agent reason about HOW
  Bricklayer = give step-by-step instructions

THE MODEL:
  General Agents → build → Custom Agents → sell as Digital FTEs
```

---

## What's Next — Core Agent Architecture

You now know *what* an agent is.

**Next (61.2):** You will learn *what's inside* an agent.

Every agent — from the simplest to the most complex — is built from the same 4 components. Together they form the **3+1 Architecture Framework**:

- **Model** — The brain (language model)
- **Tools** — The hands (what the agent can do)
- **Orchestration** — The nervous system (how it thinks and plans)
- **Deployment** — The body (how it reaches the world)

**Preparation question:**
*Before the next session — think about Claude Code. When it fixes a bug in your code, which of the 4 components above is doing what?*
