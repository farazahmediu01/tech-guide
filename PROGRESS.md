# Learning Progress Tracker

> **Goal:** Become a Senior Agentic AI Engineer in 1 year
> **Roadmap:** [The AI Agent Factory — Panaversity](https://agentfactory.panaversity.org/) (9 Parts)
> **Start Date:** 2026-02-08
> **Target Date:** 2027-02-08

---

## Current Phase: Chapter 34 — OpenAI Agents SDK (Agent Frameworks)

### Completed Topics

| # | Date | Topic | Part | Artifacts | Notes |
|---|------|-------|------|-----------|-------|
| 1 | 2026-02-08 | Docker Fundamentals | Part 6 | `docker-practice/app_1` | Built hello-world FastAPI container |
| 2 | 2026-02-10 | Docker Layers, Multi-stage Builds, Volumes | Part 6 | `docker-practice/app_2`, `docker-workshop.md` | Learned `uv` for Python packaging in Docker |
| 3 | 2026-02-12 | Docker Workshop Write-up & LinkedIn Post | Part 6 | `docker-practice/DOCKER_WORKSHOP.md`, `LINKEDIN_POST.md` | Documented learnings, shared publicly |
| 4 | 2026-02-16 | Claude Code as Learning Coach | Meta | `PROGRESS.md`, `learning_tracker.xlsx` | Set up progress tracking system |
| 5 | 2026-02-25 | Ch.34 L0-L1: SDK Setup & First Agent | Ch.34 | `openai-agents-sdk/` | Installed SDK, built first agent with Runner |
| 6 | 2026-03-08 | Ch.34 L2: Function Tools & Context Objects | Ch.34 | `openai-agents-sdk/00_practice.py`, `task_management_agent.py`, `01_support_desk_assistant.py`, `02_sro_agent.py`, `clients.py`, `cotext-in-runner.py` | Built TaskManager, Support Desk Assistant, SRO Agent — all with function tools + RunContextWrapper |
| 7 | 2026-03-30 | Claude Ecosystem, Spec-Kit, GStack | Meta/Tools | `notes/claude-ecosystem-spec-driven-development.md` | Deep dive into SDD tools; learned how Spec-Kit + GStack fit into agentic AI workflow |

### In Progress

| Topic | Started | Status | Blockers |
|-------|---------|--------|----------|
| Ch.34 L3: Agents as Tools & Multi-Agent Orchestration | 2026-03-30 | Up next | — |

### Up Next

| Priority | Topic | Why | Prerequisite |
|----------|-------|-----|-------------|
| 1 | Ch.34 L3: Agents as Tools & Multi-Agent Orchestration | Core pattern for Digital FTE systems | L2 done |
| 2 | Ch.34 L4: Agent Handoffs & Message Filtering | Enables routing between specialist agents | L3 done |
| 3 | Ch.34 L5: Guardrails & Validation | Production safety for agents | L4 done |

---
## Skills Inventory

| Skill | Level | Evidence |
|-------|-------|----------|
| Docker (basics) | Beginner | Built 2 containerized apps, wrote workshop doc |
| Python | Beginner-Intermediate | Simple FastAPI apps |
| Claude Code | Beginner-Intermediate | Workspace, CLAUDE.md, learning workflow, published to GitHub |
| Git/GitHub | Beginner | Version control, remote push to farazahmediu01/tech-guide |
| OpenAI Agents SDK | Beginner-Intermediate | 3+ agents built: TaskManager, Support Desk, SRO. Function tools, RunContextWrapper, multi-file structure |
| Pydantic | Beginner | BaseModel, Field validation, StrEnum |
| Spec-Driven Development | Awareness | Understands SDD philosophy, Spec-Kit workflow, GStack roles, and how to apply to learning |

---

## Session Log

### Session 7 — 2026-03-30
- **Focus:** Ecosystem orientation + project snapshot
- **Done:**
  - Published repo to GitHub (`farazahmediu01/tech-guide`) — first remote push
  - Researched markdown-to-presentation tools (Marp, Slidev, Reveal.js, Gamma)
  - Deep dive: Claude ecosystem layers, MCP, workflow tools
  - Compared Spec-Kit (GitHub) vs GStack (Garry Tan / YC) for SDD
  - Planned how to integrate Spec-Kit + GStack into per-lesson learning loop
  - Saved ecosystem notes, updated all tracking files
- **Next:** Ch.34 L3 — Agents as Tools & Multi-Agent Orchestration (apply Spec-Kit `/specify` before coding)

### Session 6 — 2026-03-08
- **Focus:** Ch.34 L2 — Function Tools & Context Objects
- **Done:** Built TaskManager, Support Desk Assistant, and SRO agents across multiple files. Fixed Field validation, task ID assignment, NameError, missing decorator
- **Next:** Ch.34 L3 — Agents as Tools & Multi-Agent Orchestration

### Session 5 — 2026-02-25
- **Focus:** Ch.34 L0-L1 — SDK setup, first agent
- **Done:** Installed OpenAI Agents SDK, built first agent with Runner.run_sync, explored Agent + model config
- **Next:** Function tools and context objects

### Session 4 — 2026-02-16
- **Focus:** Setting up Claude Code as a learning coach
- **Done:** Created progress tracking system (PROGRESS.md + Excel), updated CLAUDE.md, configured cross-session memory
- **Next:** Docker Compose & Networking

### Session 3 — 2026-02-12
- **Focus:** Docker workshop documentation
- **Done:** Wrote detailed workshop guide, created LinkedIn post
- **Next:** Set up learning tracking system

### Session 2 — 2026-02-10
- **Focus:** Docker layers, multi-stage builds, volumes
- **Done:** Built app_2 with multi-stage Dockerfile using uv, learned about volumes
- **Next:** Document learnings

### Session 1 — 2026-02-08
- **Focus:** Project setup, Docker fundamentals
- **Done:** Created CLAUDE.md, built first Docker container (app_1)
- **Next:** Docker layers and multi-stage builds

---

## Milestones

- [ ] **Month 1 (Feb):** Docker + Docker Compose mastery, first FastAPI project
- [ ] **Month 2 (Mar):** Python deep dive, OpenAI Agents SDK hello-world
- [ ] **Month 3 (Apr):** First working AI agent deployed in Docker
- [ ] **Month 6 (Aug):** 3+ agents in portfolio, Kubernetes basics
- [ ] **Month 9 (Nov):** Full-stack agent with UI (TypeScript), Dapr integration
- [ ] **Month 12 (Feb 2027):** Senior-level portfolio with 5+ deployed agents
