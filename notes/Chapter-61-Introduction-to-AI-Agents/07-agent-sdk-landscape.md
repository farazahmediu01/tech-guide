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

# Chapter 61.7 — The Agent SDK Landscape
## Student Learning Guide
**Source:** Agent Factory — Panaversity
**URL:** agentfactory.panaversity.org/docs/Building-Agent-Factories/introduction-to-ai-agents

---

## What You Will Learn

By the end of this guide you will be able to:

- Name the 4 major agent SDKs and their core design philosophy
- Match a problem type to the right SDK using the selection framework
- Explain what "Handoff-Centric", "Service-Centric", "Capability-Centric", and "Conversation-Centric" mean
- Describe the 3 decision questions for choosing a framework
- Explain why the 3+1 Architecture and 5-Step Loop apply to ALL SDKs

> **Why this matters:** You are learning OpenAI Agents SDK in Chapter 34. This chapter shows you the entire landscape so you understand WHERE that SDK fits and WHEN to use something else.

---

## The Big Picture — 4 Frameworks

```
┌──────────────────────────────────────────────────────────────┐
│                   AGENT SDK LANDSCAPE (2026)                  │
├──────────────────┬──────────────────────────────────────────┤
│   SDK            │   Core Philosophy                         │
├──────────────────┼──────────────────────────────────────────┤
│ OpenAI Agents SDK│ Handoff-Centric — routing and triage      │
│ Google ADK       │ Service-Centric — enterprise processes     │
│ Anthropic Kit    │ Capability-Centric — autonomous execution  │
│ Microsoft MAF    │ Conversation-Centric — collaborative teams │
└──────────────────┴──────────────────────────────────────────┘
```

> **Important:** These are not competing products you must choose between forever. A production system may use multiple frameworks for different agents within the same system.

---

## SDK 1 — OpenAI Agents SDK

### Core Philosophy: Handoff-Centric

**The main concept:** Agents hand off tasks to other agents. One agent does its part, then explicitly transfers control to the next.

```python
# OpenAI Agents SDK style — explicit handoffs
from agents import Agent, handoff

triage_agent = Agent(
    name="TriageAgent",
    instructions="Classify customer requests and hand off to the right specialist.",
    handoffs=[billing_agent, technical_agent, returns_agent]
)

billing_agent = Agent(
    name="BillingAgent",
    instructions="Handle all billing-related queries."
)
```

**Key characteristics:**
- Lightweight Python and Node.js SDK
- Simple, clean API — easy to learn
- Best for: routing, triage, specialist transfer
- Ideal for: customer support, helpdesk, classification systems

---

## SDK 1 — OpenAI Agents SDK — Strengths & Limits

<!-- _class: invert small -->

| Dimension | Detail |
|-----------|--------|
| **Core pattern** | Handoff — explicit transfer of control between agents |
| **Languages** | Python, Node.js |
| **Complexity** | Low — fastest to get started |
| **State management** | Conversation context passed through handoffs |
| **Multi-agent** | Yes — via explicit handoff declarations |
| **Best strength** | Clean routing logic, simple specialist transfers |
| **Ideal use case** | Customer support routing, FAQ triage, intake systems |
| **Not ideal for** | Long-running enterprise processes, artifact-heavy workflows |

**Real-world scenario it handles best:**
> A user contacts support. They have a billing issue AND a technical issue. The Triage Agent identifies both problems and hands off to the Billing Agent and Technical Agent in sequence.

**This is exactly what you are building in Chapter 34.**

---

## SDK 2 — Google ADK (Agent Development Kit)

### Core Philosophy: Service-Centric

**The main concept:** Agents are modeled as services with well-defined inputs, outputs, and state managed through artifacts (structured data objects).

```python
# Google ADK style — artifact-based state
from google.adk import Agent, Artifact

invoice_processor = Agent(
    name="InvoiceProcessor",
    input_schema=InvoiceArtifact,
    output_schema=ProcessedInvoiceArtifact,
    services=["google_sheets", "gmail", "drive"]
)
```

**Key characteristics:**
- TypeScript and Pydantic schemas for strict data contracts
- Artifact-based state management — data flows as typed objects
- Deep integration with Google Cloud services
- Best for: structured enterprise workflows, data processing pipelines

---

## SDK 2 — Google ADK — Strengths & Limits

<!-- _class: invert small -->

| Dimension | Detail |
|-----------|--------|
| **Core pattern** | Service — each agent is a typed service with strict schema |
| **Languages** | TypeScript, Python (Pydantic) |
| **Complexity** | Medium — strong typing requires upfront schema design |
| **State management** | Artifacts — structured data objects passed between agents |
| **Multi-agent** | Yes — agents consume each other's artifact outputs |
| **Best strength** | Enterprise-grade data integrity, Google Cloud integration |
| **Ideal use case** | Invoice processing, HR workflows, compliance pipelines |
| **Not ideal for** | Rapid prototyping, creative or open-ended tasks |

**Real-world scenario it handles best:**
> An enterprise HR system where an agent extracts data from a form, validates it against a schema, writes to Google Sheets, triggers an approval workflow, and sends a confirmation email — all with typed data contracts at every step.

---

## SDK 3 — Anthropic Agents Kit

### Core Philosophy: Capability-Centric

**The main concept:** Agents are defined by what they can **do** — their capabilities. The MCP (Model Context Protocol) standard connects these capabilities to real-world tools and data.

```python
# Anthropic style — capability and MCP tool focus
from anthropic import Agent
from mcp import MCPToolset

research_agent = Agent(
    model="claude-3-5-sonnet",
    capabilities=["web_search", "code_execution", "file_analysis"],
    mcp_tools=MCPToolset([
        "filesystem", "github", "web_search", "computer_use"
    ])
)
```

**Key characteristics:**
- Powered by Claude models
- MCP tools as the integration standard (75+ connectors)
- Computer Use — can control a browser or desktop
- Best for: autonomous coding, research, data analysis

---

## SDK 3 — Anthropic Agents Kit — Strengths & Limits

<!-- _class: invert small -->

| Dimension | Detail |
|-----------|--------|
| **Core pattern** | Capability — what the agent can DO defines its identity |
| **Languages** | Python |
| **Complexity** | Medium — MCP configuration required |
| **State management** | Context window + MCP tool state |
| **Multi-agent** | Yes — via MCP server chaining |
| **Best strength** | Autonomous task execution, MCP ecosystem, Computer Use |
| **Ideal use case** | Coding agents, research agents, data analysis, browser automation |
| **Not ideal for** | Structured enterprise data pipelines, strict handoff routing |

**Real-world scenario it handles best:**
> A research agent that searches the web, reads PDFs, opens a browser to fill in a form, writes a Python script to analyze data, and produces a final report — all autonomously.

**This is Claude Code's internal architecture.**

---

## SDK 4 — Microsoft Agent Framework (MAF)

### Core Philosophy: Conversation-Centric

**The main concept:** Multiple agents participate in a **group chat**, collaborating through conversation. Each agent has a persona and contributes to the discussion.

```python
# Microsoft Agent Framework style — group chat
from microsoft.agents import GroupChat, AgentPersona

product_review = GroupChat(
    agents=[
        AgentPersona("ProductManager", "Evaluate from user perspective"),
        AgentPersona("Engineer", "Evaluate technical feasibility"),
        AgentPersona("Designer", "Evaluate UX and visual quality"),
        AgentPersona("QA", "Identify edge cases and risks")
    ],
    topic="Review the new checkout flow design"
)
```

**Key characteristics:**
- Agents collaborate through structured conversation
- Multi-perspective problem solving
- Best for: design reviews, brainstorming, multi-stakeholder decisions

---

## SDK 4 — Microsoft Agent Framework — Strengths & Limits

<!-- _class: invert small -->

| Dimension | Detail |
|-----------|--------|
| **Core pattern** | Conversation — agents collaborate via group chat |
| **Languages** | Python, .NET, TypeScript |
| **Complexity** | Medium-High — persona design requires thought |
| **State management** | Conversation history as shared state |
| **Multi-agent** | Yes — core feature, not an add-on |
| **Best strength** | Multi-perspective analysis, collaborative decision-making |
| **Ideal use case** | Code review panels, product design simulation, risk assessment |
| **Not ideal for** | Routing/triage, strict sequential pipelines |

**Real-world scenario it handles best:**
> A company is evaluating a new product feature. Four agents — PM, Engineer, Designer, and QA — discuss it from their perspectives in a group chat. The result is a balanced, multi-perspective recommendation.

---

## Framework Comparison Matrix

<!-- _class: invert small -->

| Dimension | OpenAI SDK | Google ADK | Anthropic Kit | Microsoft MAF |
|-----------|-----------|-----------|--------------|--------------|
| **Core pattern** | Handoff | Service | Capability | Conversation |
| **Best for** | Routing, triage | Enterprise pipelines | Autonomous tasks | Multi-perspective |
| **Languages** | Python, Node | TS, Python | Python | Python, .NET, TS |
| **Complexity** | Low | Medium | Medium | Medium-High |
| **State mgmt** | Conversation | Artifacts | Context + MCP | Chat history |
| **Multi-agent** | Handoffs | Artifact flow | MCP chaining | Group chat |
| **Learning curve** | Gentlest | Moderate | Moderate | Steepest |

---

## The 3 Decision Questions

Before choosing a framework, answer these questions:

```
Question 1: What is the PRIMARY interaction pattern?

  Routing different request types to specialists?  → OpenAI Agents SDK
  Processing structured data through a pipeline?   → Google ADK
  Executing autonomous, open-ended tasks?          → Anthropic Agents Kit
  Collaborative multi-perspective problem solving? → Microsoft MAF

Question 2: How do you describe your agent's work?

  "It hands off to the right agent"    → OpenAI Agents SDK
  "It processes this type of data"     → Google ADK
  "It uses these tools to do X"        → Anthropic Agents Kit
  "It collaborates with other agents"  → Microsoft MAF

Question 3: What is your deployment context?

  Cloud-agnostic, lightweight          → OpenAI Agents SDK
  Google Cloud ecosystem               → Google ADK
  MCP tools, browser automation        → Anthropic Agents Kit
  Microsoft Azure, enterprise .NET     → Microsoft MAF
```

---

## Try It Yourself — SDK Selection

Match each scenario to the right SDK. Justify your answer.

1. A **customer support system** that routes billing queries to a Billing Agent, tech queries to a Tech Agent, and returns to a Returns Agent.

2. An **automated HR onboarding pipeline** that processes new employee forms, validates data against schemas, creates accounts in Google Workspace, and sends welcome emails.

3. A **research assistant** that searches the web, reads 10 articles, writes Python code to analyze data, and produces a formatted report — all without being told each step.

4. A **product design review** where agents representing the PM, Engineer, and UX Designer evaluate a new feature from their respective perspectives.

5. **Challenge:** A company needs a system where a Triage Agent routes requests, but the Technical Support Agent autonomously browses documentation to find answers. Which combination of SDKs would you use?

---

## What All Frameworks Share — The Universal Foundation

**This is critical:** The SDK changes. The underlying principles never do.

```
UNIVERSAL ACROSS ALL 4 FRAMEWORKS:

✓ 3+1 Architecture (Model, Tools, Orchestration, Deployment)
  Every framework implements these 4 components

✓ 5-Step Loop (Plan, Act, Observe, Update, Evaluate)
  Every agent runs this loop regardless of SDK

✓ Multi-Agent Patterns (Coordinator, Sequential, Iterative, HITL)
  All 4 patterns are implementable in all 4 frameworks

✓ Agent Ops (Golden Datasets, Traces, LM-as-Judge, KPIs)
  Production requirements don't change with the SDK

✓ Security (Least Privilege, Defense in Depth, Agent Identity)
  Security principles are framework-agnostic
```

> **Learn the principles deeply. The SDKs are just syntax.**

---

## Common Mistakes

<!-- _class: invert small -->

| Mistake | Wrong Thinking | Reality |
|---------|---------------|---------|
| "OpenAI SDK is always the best because it's from OpenAI" | Brand = quality | Each SDK is designed for different use cases |
| "I must pick one SDK for everything" | Lock-in is required | Production systems mix SDKs for different agents |
| "Google ADK is only for Google users" | Cloud-specific | ADK can run outside Google Cloud with adapters |
| "Anthropic Kit only works with Claude" | Model lock-in | Can integrate other models, but Claude is primary |
| "The SDK with the most features wins" | More = better | Choose the SDK that fits your problem pattern |
| "Learning one SDK means learning all" | They're all the same | Different paradigms, different mental models |

---

## Quick Reference Card

```
THE 4 AGENT SDKs

OpenAI Agents SDK  → HANDOFF-CENTRIC
  Best for: Routing, triage, specialist transfer
  Languages: Python, Node.js | Complexity: Low

Google ADK         → SERVICE-CENTRIC
  Best for: Enterprise data pipelines, typed workflows
  Languages: TypeScript, Python | Complexity: Medium

Anthropic Agents   → CAPABILITY-CENTRIC
  Best for: Autonomous tasks, MCP tools, browser automation
  Languages: Python | Complexity: Medium

Microsoft MAF      → CONVERSATION-CENTRIC
  Best for: Multi-perspective analysis, collaborative decisions
  Languages: Python, .NET, TS | Complexity: Medium-High

3 DECISION QUESTIONS:
  1. What is the primary interaction pattern?
  2. How do you describe your agent's work?
  3. What is your deployment context?

UNIVERSAL TRUTH: 3+1 Architecture, 5-Step Loop, Agent Ops,
and Security principles apply to ALL frameworks.
```

---

## What's Next — Your First Agent Concept

You have learned the complete theory of AI agents.

**Next (61.8):** You will apply everything and write your **first real agent specification**.

This is where theory becomes practice:
- Use the 5-section Agent Spec Template
- Define your agent's Level, Architecture, Process, Pattern, and Security
- Test your spec with AI validation
- This spec becomes the foundation for your first real build

**Preparation question:**
*Think of one repetitive task at Aptech Institute that takes time — grading, attendance, answering student questions, scheduling. Pick one. What would an AI agent version of that look like?*
