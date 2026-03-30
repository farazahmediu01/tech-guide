---
marp: true
---

# Claude Ecosystem & Spec-Driven Development
### Spec-Kit vs GStack — Deep Comparison

---

## 1. The Claude Ecosystem (2026)

```
┌─────────────────────────────────────────────────────────────┐
│                    CLAUDE CODE ECOSYSTEM                     │
├──────────────────┬──────────────────┬───────────────────────┤
│  FOUNDATION      │  WORKFLOW LAYER  │  INTEGRATION LAYER    │
│                  │                  │                        │
│  Claude Code     │  Spec-Kit        │  MCP (75+ connectors) │
│  (core agent)    │  GStack          │  LangGraph             │
│                  │  Superpowers     │  CrewAI                │
│  Claude Agent    │  cc-sdd          │  Mastra (TypeScript)   │
│  SDK             │  Kiro (AWS IDE)  │  Microsoft Agent Fwk   │
└──────────────────┴──────────────────┴───────────────────────┘
```

**Key 2026 shift:** Claude Code is no longer a "chat assistant." It's a full agentic system — it reads files, writes code, runs terminals, calls tools, and can orchestrate other agents. The ecosystem around it is now about **how you structure that agency** — which is exactly where Spec-Kit and GStack come in.

---

## 2. What is Spec-Driven Development?

> **Spec = a contract for how your code should behave, written before a single line of code.**

In traditional development:
```
Idea → Code → (maybe) Docs → Test
```

In Spec-Driven Development (SDD):
```
Idea → Spec → Plan → Tasks → AI implements → Review
```

The spec becomes the **single source of truth**. The AI doesn't guess your intent — it reads the spec and builds to it. This is critical for agents because:

- AI hallucinates without constraints → specs are constraints
- Agents need deterministic checkpoints → specs provide them
- Code reviews become spec compliance checks, not opinion debates
- You can swap AI models without losing intent

A January 2026 arXiv paper formally defines three SDD rigor levels:

| Level | Name | Description |
|-------|------|-------------|
| 1 | Spec-First | Write spec, then code (loosely coupled) |
| 2 | Spec-Anchored | Spec is referenced throughout implementation |
| 3 | Spec-as-Source | Code is *generated* from the spec (highest rigor) |

Both Spec-Kit and GStack target **Level 2-3**.

---

## 3. Spec-Kit (by GitHub)

**"Specification as the center of your engineering process"**

Open-sourced by GitHub in September 2025. 28K+ stars. MIT licensed.

### Core Workflow — 4 Phases

```
/specify  →  /plan  →  /tasks  →  /implement
```

| Phase | What happens |
|-------|-------------|
| `/specify` | You give a high-level prompt → AI generates a full spec (what & why) |
| `/plan` | You give technical direction → AI generates implementation plan |
| `/tasks` | Spec is broken into small, reviewable, independently testable units |
| `/implement` | AI implements task by task; you review each |

### Philosophy
Spec is the primary artifact. Code is a **derived output**. The developer's role is to **steer**, not to type.

### Tooling
- Shell scripts (Unix) + PowerShell (Windows) — works anywhere
- VS Code extension with DAG visualization and task checklist
- Supports Claude, Copilot, Gemini, OpenAI, Cursor, Windsurf
- Claude-specific template packages available

---

## 4. GStack (by Garry Tan — YC President)

**"Turn Claude Code into a Virtual Software Development Team"**

Released March 2026. Hit **10,000 stars in 48 hours** — one of the fastest-growing dev tools ever.

### Core Concept

Instead of one AI doing everything, GStack assigns **specialist roles** to Claude via slash commands:

```
/plan-review    → Engineering Manager
/code-review    → Senior Engineer
/ship           → Release Manager
/qa             → QA Engineer
/browser        → Browser Automation Specialist
/retro          → Engineering Retrospective Lead
```

### Philosophy
Software delivery is a **team sport**. GStack simulates the checks and handoffs of a real engineering team — planning, reviewing, shipping, testing — all inside Claude Code.

### Results (Garry Tan's personal numbers)
- **10,000 lines of code/week**
- **100 PRs/week**
- Maintained at **production quality** over a 50-day stretch

---

## 5. Side-by-Side Comparison

| Dimension | Spec-Kit | GStack |
|-----------|----------|--------|
| **Created by** | GitHub | Garry Tan (YC) |
| **Core metaphor** | Spec as source of truth | Virtual dev team |
| **Entry point** | Write a spec first | Start with a plan or code |
| **Primary focus** | *What* to build (specification) | *How* to ship it (workflow) |
| **Workflow style** | Sequential phases with checkpoints | Role-based slash commands |
| **AI autonomy level** | Medium (human steers each phase) | High (agent acts like a team) |
| **Best for** | New projects, unclear requirements | Active projects, shipping fast |
| **Output artifact** | Spec document + task list | PRs, reviews, QA reports |
| **IDE support** | VS Code + any terminal | Claude Code native |
| **SDD rigor level** | Level 2-3 (Spec-Anchored to Spec-as-Source) | Level 2 (Spec-Anchored) |
| **Stars** | 28K+ | 10K+ (in 48hrs) |

---

## 6. When to Use Each

**Use Spec-Kit when:**
- Starting a **new project** from scratch
- Requirements are ambiguous and need to be clarified first
- You want a **documented spec** as a deliverable (client work, teams)
- Working in a team where multiple people need to understand the plan
- You want to enforce spec compliance across AI model swaps

**Use GStack when:**
- You already have a codebase and want to **ship faster**
- You need structured **code review and QA** baked into your workflow
- Solo developer trying to simulate team-level rigor
- You're iterating rapidly (startup pace, MVP mode)
- You want opinionated, proven workflow defaults from day one

**Use both together (advanced):**
```
Spec-Kit (specify → plan → tasks)
         ↓
GStack (/code-review → /ship → /qa)
```
Spec-Kit handles the *front-end* of the process (what to build), GStack handles the *back-end* (how to ship it reliably). This is the emerging best practice in the community.

---

## 7. Roadmap Connection

This maps to **Chapter 16** of the Agent Factory curriculum — *Spec-Driven Development with Claude Code*. The OpenAI Agents SDK skills being built now (agent design, tool use, context management) are the foundation that makes SDD powerful: specs will be used to orchestrate multi-agent pipelines, not just single features.

---

## Sources

- [GitHub Spec Kit Repo](https://github.com/github/spec-kit)
- [GitHub Blog: Spec-Driven Development with AI](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/)
- [GStack GitHub (Garry Tan)](https://github.com/garrytan/gstack)
- [GStack Overview](https://gstacks.org/)
- [Garry Tan's GStack: Running Claude Like an Engineering Team](https://agentnativedev.medium.com/garry-tans-gstack-running-claude-like-an-engineering-team-392f1bd38085)
- [Spec-Driven Development 2026 Guide](https://www.productbuilder.net/learn/spec-driven-development)
- [Agent Factory — Chapter 16: Spec-Driven Development](https://agentfactory.panaversity.org/docs/General-Agents-Foundations/spec-driven-development)
- [Superpowers vs GStack Comparison](https://particula.tech/blog/superpowers-vs-gstack-ai-coding-skill-packs)
