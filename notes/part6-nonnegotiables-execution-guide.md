# Part 6 "Building Agent Factories" — Non-Negotiables Execution Guide

> **Date:** 2026-06-12
> **Target:** Market-Ready Senior Agentic AI Architect by Jan–Feb 2027
> **Pace assumption:** 12–15 hrs/week, 3 fixed sessions/week (2 weeknights + 1 weekend)
> **Companion docs:** `notes/agentic-ai-architect-strategy-2026-06.md` (full strategy) · `~/.claude/plans/velvety-noodling-reddy.md` (Ch62 dual-track plan)
> **Rule:** Every step ends with a proof artifact. No artifact = step not done, regardless of hours spent.

---

## 1. The Core Insight

Out of Part 6's 18 chapters, only **8 are non-negotiable**. They form the lifecycle of a production agent:

```
BUILD (Ch62) → CONNECT (Ch66–67) → SERVE (Ch70, 74) → PROVE (Ch76–77, 69)
```

Drop any one and the chain breaks. Everything else is a skim, a second framework deferred until the first is mastered, or résumé theater.

---

## 2. Tier Map — All 18 Chapters Triaged

| Tier | Chapters | Role |
|------|----------|------|
| **Tier 1 — Master** | 62, 66, 67, 70, 74, 76, 77, 69 (+ Ch73 fundamentals only) | The non-negotiable core |
| **Tier 2 — Second pass** | 64, 65, 75, 68 | Important; do after Tier 1 foundations |
| **Skim** | 61 (one sitting), 63 (awareness only), 73-advanced | Fluency, not depth |
| **Skip / on-demand** | 71, 72, 78 (defer), 63 (deep) | Learn the week a job/client demands it |

---

## 3. Step-by-Step Execution Plan

### Step 1 — Framework Mastery: Ch62 OpenAI Agents SDK
**Duration: 6 weeks (Weeks 1–6) · ~75 hrs**

| # | Topic | Detail | Sessions | Proof artifact |
|---|-------|--------|----------|----------------|
| 1.1 | L4 — Handoffs & message filtering | `handoff()` vs agent-as-tool; when to transfer control vs stay in control; input filters | 2 | Generic handoff demo + Spendly ExpenseAgent↔InsightsAgent `handoff()` |
| 1.2 | L5 — Guardrails | `@input_guardrail` / `@output_guardrail`, tripwires, agent-based validation | 2 | PII guardrail demo + Spendly card-number input guardrail & cross-user-leak output guardrail |
| 1.3 | L6 — Sessions & memory | `SQLiteSession`, multi-turn state, session keying | 2 | Session demo + Spendly sessions keyed by `user_phone` |
| 1.4 | L7 — Tracing, hooks, observability | `RunHooks`, `trace()`, `RunConfig`, structured logging | 2 | Hooks demo + JSON logging in Spendly's WhatsApp pipeline |
| 1.5 | L8 — MCP integration (consumer side) | `MCPServerStdio`, `HostedMCPTool` — *using* MCP, building comes in Step 2 | 1–2 | Minimal MCP client demo |
| 1.6 | L9 — RAG with FileSearchTool | Vector stores, retrieval inside the SDK | 1–2 | FAQ RAG demo |
| 1.7 | L10 — Capstone | Customer Support Digital FTE per official spec | 3–4 | Capstone passes its full validation checklist (PII block, refund routing, RAG citation) |

**Mastery bar:** Capstone checklist passes AND Spendly visibly contains `handoff()`, guardrails, `SQLiteSession`, `RunHooks`.

---

### Step 2 — Protocols & Serving Layer: Ch66–67 (MCP) + Ch70 (FastAPI) + Ch64–65 (Claude)
**Duration: 6 weeks (Weeks 7–12) · ~75 hrs**

| # | Topic | Detail | Sessions | Proof artifact |
|---|-------|--------|----------|----------------|
| 2.1 | Ch66 — MCP fundamentals | Protocol architecture: resources, tools, prompts, transports. Why every vendor converged on it | 2 | Working stdio MCP server (toy) |
| 2.2 | Ch67 — Custom MCP servers | Production server: auth, error handling, schema design | 3 | **Published MCP server exposing Spendly's `query_expenses` / `get_insights`** |
| 2.3 | Ch70 — FastAPI for agents | Async patterns, streaming responses, webhooks, request/response models, background tasks | 3 | Spendly backend refactored: typed models, proper webhook handling, off ngrok onto Railway/Render |
| 2.4 | Ch64 — Claude API | Agentic loops, structured output, batch processing (second framework begins) | 2 | Python agent loop **from scratch, no SDK** (ChaiCode-replica #1) using Claude API |
| 2.5 | Ch65 — Claude Agent SDK | Subagents, hooks, skills — backend for software-dev agents (your domain) | 2 | One small dev-agent built on Claude Agent SDK |
| 2.6 | Ch68 — Agent Skills & MCP code execution | Fast follow once 66–67 are done | 1 | Skill-enabled agent demo |

**Mastery bar:** You can explain MCP's architecture on a whiteboard and have a published server to point at. Spendly is on real hosting.

---

### Step 3 — Data & Memory: Ch74 (SQLModel) + Ch73 (RAG) + Ch75 (Memory)
**Duration: 5 weeks (Weeks 13–17) · ~65 hrs**

| # | Topic | Detail | Sessions | Proof artifact |
|---|-------|--------|----------|----------------|
| 3.1 | Ch74 — SQLModel & relational DBs | Typed models, async sessions, migrations, relationships | 3 | Spendly migrated aiosqlite → **PostgreSQL via SQLModel** with migrations |
| 3.2 | Ch73 — Vector DBs & RAG (fundamentals) | Embeddings, chunking, retrieval, hybrid search, **when RAG is the wrong tool** | 3 | Financial-literacy RAG knowledge base for Spendly's Insights agent |
| 3.3 | Vectorless retrieval (off-roadmap) | PageIndex-style retrieval in Python (ChaiCode-replica #2) | 1 | Working vectorless retrieval demo |
| 3.4 | Ch75 — Augmented memory | Per-user long-term memory; Mem0 + graph memory (ChaiCode-replica #3) | 2 | Spendly per-user memory ("user's rent is 40k, paid on 5th") |

**Mastery bar:** Spendly answers questions grounded in both its DB and a knowledge base, and remembers users across sessions.

---

### Step 4 — Quality Engineering (the senior differentiator): Ch76 + Ch77 + Ch69
**Duration: 6 weeks (Weeks 18–23) · ~75 hrs**

| # | Topic | Detail | Sessions | Proof artifact |
|---|-------|--------|----------|----------------|
| 4.1 | Ch76 — TDD for agents | Testing non-deterministic systems: mocking LLM calls, testing tools deterministically, contract tests | 3 | Test suite over Spendly's intent classifier + extraction pipeline (starts Week 1 with 5 cases — see §5) |
| 4.2 | Ch77 — Evals | Golden datasets, LLM-as-judge, regression suites. Primer: *Eval-Driven Development* crash course first | 4 | **Eval suite that gates every prompt/model change in Spendly** — the #1 senior interview topic |
| 4.3 | Ch69 — Multi-agent reliability | Error taxonomies, escalation paths, provenance, human-in-the-loop thresholds | 3 | Escalation + confidence-threshold design implemented in Spendly's pipeline |

**Mastery bar:** A prompt change that breaks extraction accuracy gets *caught by CI*, not by a user.

---

### Step 5 — Skims & Closeout
**Duration: 1 week (Week 24) · ~12 hrs**

| # | Topic | Detail | Proof artifact |
|---|-------|--------|----------------|
| 5.1 | Ch61 — Intro to AI agents | One-sitting read; you've already lived it | Notes only |
| 5.2 | Ch63 — Google ADK | Skim for pattern-mapping (80% overlaps what you know) | One-page "ADK vs OpenAI SDK" comparison note |
| 5.3 | Portfolio assembly | READMEs, demos, architecture diagrams for capstone + Spendly + MCP server | Public portfolio: 3 deployed agents + 1 monetizable product |

---

## 4. Time Summary

| Step | Focus | Weeks | Hours | Calendar (from 2026-06-15) |
|------|-------|-------|-------|---------------------------|
| 1 | Ch62 SDK mastery (L4–L10) | 6 | ~75 | Jun 15 – Jul 26 |
| 2 | MCP + FastAPI + Claude (Ch66–67, 70, 64–65, 68) | 6 | ~75 | Jul 27 – Sep 6 |
| 3 | Data & memory (Ch74, 73, 75) | 5 | ~65 | Sep 7 – Oct 11 |
| 4 | TDD + Evals + Reliability (Ch76–77, 69) | 6 | ~75 | Oct 12 – Nov 22 |
| 5 | Skims + portfolio closeout | 1 | ~12 | Nov 23 – Nov 29 |
| **Total** | **Part 6 non-negotiables** | **24** | **~300** | **Done by end of Nov 2026** |

This leaves **Dec 2026 – Jan 2027** for Part 7 selective deployment chapters (Ch79–80 Docker/K8s, Ch85 observability/cost, Ch88 security, Ch90 real deployment) — exactly Phase 4 of the strategy doc — landing the full target by **Feb 2027**.

> **Buffer reality check:** the schedule assumes 3 sessions/week, every week. Miss a week, everything slides a week. Miss two sessions in any week → cut scope (drop a Tier 2 item), never re-plan.

---

## 5. Explicit Skip List (resist the urge)

| Chapter | Topic | Why skipped | When to learn |
|---------|-------|-------------|---------------|
| Ch63 (deep) | Google ADK | Third framework fragments a still-consolidating skill base | The week a job/client requires it (~days, not weeks, once concepts are solid) |
| Ch71 | ChatKit Server | Vendor-specific UI plumbing | On demand |
| Ch72 | Apps SDK / ChatGPT apps | Niche distribution channel | On demand |
| Ch78 | GraphRAG | Genuinely interesting, genuinely deferrable | Stretch after Step 3, or when Spendly's insights need relationship queries |

---

## 6. Standing Rules

1. **Artifact or it didn't happen.** Every session ends with running code, a passing test, or a published thing.
2. **Spendly is the spine.** Every step lands a Spendly milestone — it's the portfolio centerpiece and every interview answer.
3. **One framework deeply before two shallowly.** Claude API/SDK starts only after Ch62 L10 passes its checklist.
4. **LinkedIn post per completed lesson** — the public forcing function.
5. **Tests start Week 1**, not Step 4. `whatsapp/tests/test_intent_classifier.py` with 5 cases is due this week; Ch76 formalizes the habit later.
6. **No new strategy documents** until three consecutive execution artifacts exist. This guide and the strategy doc are the last planning artifacts.

---

*Next action: Ch62 L4 — Handoffs. Entry ticket: explain why Spendly's Intent Classifier → Expense Extractor is currently orchestration (agent-as-tool), and what would change for the user if it became a true `handoff()`.*

claude --resume b23d8a63-e960-416d-ac67-815597d1c1bf