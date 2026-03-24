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
| 6 | 2026-03-08 | Ch.34 L2: Function Tools & Context Objects | Ch.34 | `openai-agents-sdk/00_practice.py` | Built TaskManager: add_task, list_tasks, complete_task with RunContextWrapper |

### In Progress

| Topic | Started | Status | Blockers |
|-------|---------|--------|----------|
| Ch.34 L2: Function Tools & Context Objects | 2026-03-08 | Reviewing & polishing | — |

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
| Claude Code | Beginner | Set up workspace, CLAUDE.md, learning workflow |
| Git/GitHub | Beginner | Using for version control |
| OpenAI Agents SDK | Beginner | First agent running, 3 function tools with RunContextWrapper |
| Pydantic | Beginner | BaseModel, Field validation, StrEnum |

---

## Session Log

### Session 6 — 2026-03-08
- **Focus:** Ch.34 L2 — Function Tools & Context Objects
- **Done:** Built TaskManager agent with 3 tools (`add_task`, `list_tasks`, `complete_task`). Multiple code review iterations — fixed Field validation, task ID assignment, NameError bug, missing decorator, renamed counter, added Agent + Runner wiring
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
