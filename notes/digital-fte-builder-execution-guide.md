# Digital FTE Builder — Execution Guide

> **Version:** 2 · **Written:** 2026-08-27 · **Runs:** 2026-08-31 → 2027-02-28 (26 weeks)
> **Supersedes:** `part6-nonnegotiables-execution-guide.md` (v1, 2026-06-12) — that file's chapter numbers are dead; its dependency chain is not. Everything of value from it is carried forward here.
> **Also consolidates:** `agentic-ai-architect-strategy-2026-06.md` (strategy) and the 2026-08 curriculum audit.
> **Target role:** **Digital FTE Builder** — the Agent Factory's stated primary graduate. FDE is the same skill set, embedded on a client site.
> **Pace:** 60–90 min/day solo · 3 × 2 hr teaching sessions/week · ~8 solo hrs/week
> **Rule:** Every phase ends with a proof artifact. No artifact = phase not done, regardless of hours spent.

**This is the only roadmap file. If a second one appears, one of them is wrong.**

---

## 1. The correction that reset this plan

v1 was written under a false belief: *"Agent Factory shifted its focus from Agentic AI Architect to Forward Deployed Engineer — the entire syllabus changed."*

Verified against the live roles page (`/roman/docs/roles-this-book-trains`, 2026-08-27):

| Role | Position in the live book |
|---|---|
| **Digital FTE Builder** | **"The book's primary graduate."** Builds the unit product end to end. |
| Outcome Architect | Core pipeline role #1 |
| AI-Native Company Architect | Core pipeline role #3 — still certified via the five-quarter program |
| **Forward Deployed Engineer** | **Supporting role #5** — the *embedded* variant of the same pipeline |

**Nothing was replaced. A role was added, and the FDE is this same skill set with a plane ticket.** The target already recorded in `CLAUDE.md` (Primary: Digital FTE Builder) was correct.

Two further facts that ended the panic:

1. **Every Tier-1 chapter from v1 survives intact** in `resources/agent-factory/archived-wayback/`. Nothing was lost. v1 died because it indexed by *chapter number*, and the site has now renumbered twice.
2. **The archive is the only surviving copy** of the deep-engineering half of the book. FastAPI depth, SQLModel, TDD, multi-agent reliability, Claude API / Agents Kit, Google ADK, GraphRAG, memory, and the entire Docker/K8s/Helm/Dapr/Kafka/ArgoCD cloud part exist **nowhere on the live site**. Guard it, `MANIFEST.tsv` included.

---

## 2. The core insight (carried forward from v1, unchanged)

The lifecycle of a production agent. Drop any link and the chain breaks:

```
BUILD → CONNECT → SERVE → PROVE → DEPLOY
```

The 2026-08 audit found the live book independently reproduces this order (Phase 2 = BUILD · C28/C33 = CONNECT + data · C41 = SERVE · C40 = PROVE). Two documents, written a year apart by different people, converged on the same sequence.

**The sequence is right. Only the addresses changed.**

---

## 3. The slug index — replaces the dead chapter-number tier map

Chapter numbers have changed twice. **Slugs survived both.** Index by slug, permanently.

### 3.1 Archive (depth source) — `resources/agent-factory/archived-wayback/`

| v1 called it | Lives at | Tier |
|---|---|---|
| Ch62 OpenAI Agents SDK | `Building-Agent-Factories/openai-agents-sdk/` **+ `chapter-34-openai-agents-sdk/Openai Agents Sdk.md`** | 1 |
| Ch66 MCP fundamentals | `Building-Agent-Factories/mcp-fundamentals/` | 1 |
| Ch67 Custom MCP servers | `Building-Agent-Factories/custom-mcp-servers/` | 1 |
| Ch70 FastAPI for agents | `Building-Agent-Factories/fastapi-for-agents/` | 1 |
| Ch74 Relational DBs / SQLModel | `Building-Agent-Factories/relational-databases-sqlmodel/` | 1 |
| Ch76 TDD for agents | `Building-Agent-Factories/tdd-for-agents/` | 1 |
| Ch77 Evals | `Building-Agent-Factories/evals-agent-performance/` | 1 |
| Ch69 Multi-agent reliability | `Building-Agent-Factories/multi-agent-reliability.md` | 1 |
| Ch73 Vector DBs & RAG | `Building-Agent-Factories/vector-databases-rag-langchain/` | **dropped — see §4.3** |
| Ch75 Augmented memory | `Building-Agent-Factories/augmented-memory/` | 2 |
| Ch64 / Ch65 Claude API / Agents Kit | `claude-api-agentic-loops.md` · `anthropic-agents-kit-development/` | 2 |
| Ch68 Skills & MCP code execution | `agent-skills-mcp-code-execution/` | 2 |
| Cloud (Phase 4) | `Deploying-Agent-Factories-in-the-Cloud/` → `docker-for-ai-services/` · `observability-cost-engineering/` · `production-security/` · `cicd-gitops-argocd/` · `event-driven-kafka/` | 1–2 |

**Use the full-chapter file, not the folder.** `chapter-34-openai-agents-sdk/Openai Agents Sdk.md` (4,785 lines) holds all 12 SDK lessons — including Handoffs (L4), Function Tools (L2) and RAG/FileSearchTool (L9), which are **absent** from the archive's `openai-agents-sdk/` folder.

### 3.2 Live book (currency source) — `agentfactory.panaversity.org`

| # | Course | Slug | Used in |
|---|---|---|---|
| 28 | Searchable Context: RAG on Postgres + pgvector | `/docs/postgres-ai-crash-course` | Phase 2 |
| 32 | Build AI Agents | `/docs/build-agents-crash-course` | Phase 1 |
| 33 | From Agent to Digital FTE | `/docs/digital-fte-crash-course` | Phase 2 |
| 40 | Eval-Driven Development | `/docs/eval-driven-development-crash-course` | Phase 3 |
| 41 | Deploy Your Agent Harness to the Cloud | `/docs/deploying-agents-crash-course` | Phase 4 |
| 42 | Choosing Agentic Architectures | `/docs/choosing-agentic-architectures-crash-course` | Phase 5 |

### 3.3 Teaching source

`C:\Users\Faraz\Desktop\agentic-ai-from-scratch\` — **Agent SDK Fluency, Ch0–6 only.** Ch7–12 are never authored (§7).

---

## 4. Source-of-truth rule

> **Archive = depth. Live crash courses = currency. Your Ch0–6 = teaching. When the site moves again, change nothing.**

### 4.1 What the archive teaches better — use it

FastAPI depth (14 sections: JWT auth, DI, middleware/CORS, SSE streaming, lifespan events, error handling, password hashing) · SQLModel · TDD/pytest for agents · multi-agent reliability · eval pedagogy (dataset design, LLM-as-judge, regression protection, systematic error analysis, the two evaluation axes) · Docker · the whole cloud-native part.

**The live book teaches none of this.**

### 4.2 What only the live book has — Tier A, verified absent from the archive by grep

| Delta | Archive hits |
|---|---|
| `SandboxAgent` + `Capabilities.default()` | 0 |
| `@function_tool(needs_approval=True)` — HITL gates | 0 |
| `@tool_input_guardrail` — the **third** guardrail type | 0 |
| Harness/sandbox split (SDK-enforced since April 2026) | 0 |
| Neon + `pgvector` as system of record | 0 |
| `agentskills.io` format + progressive disclosure | 0 |
| Inngest durable execution | 0 |
| DeepEval · Azure Container Apps · E2B | 0 |

The archive snapshot is dated **2026-05-21** and its SDK chapter predates that. Building from it alone produces a 2025-shaped agent.

### 4.3 The five amendments (v1 → v2)

| # | Amendment | Effect |
|---|---|---|
| 1 | Index by **slug**, never by chapter number | Survives the next renumber |
| 2 | Phase 1: read **C32** once as a delta list; add 3 SDK mechanisms to Spendly | +3.5 h |
| 3 | Phase 2: data layer from **C28 + C33**; **drop** archive `vector-databases-rag-langchain` (LangChain-era). Keep archive FastAPI — better, and the only copy | −2 h |
| 4 | Phase 3: archive evals = pedagogy; **C40** = 9-layer coverage checklist + 4-tool chain | +6 h |
| 5 | Phase 4: deploy path from **C41**; keep archive Docker. K8s/Helm/Dapr/Kafka stay deferred — **the live book explicitly declines to teach them too** | +2 h |

Plus one addition: **C42 Reader track, Week 26.**

Net: **~+13 h added, ~4 h saved, across 26 weeks.** The plan's shape, phases and dates do not change.

---

## 5. The 26-week execution plan

Model: **you learn a topic, you teach it two weeks later from the same artifacts.** Your build is the answer key.

### Phase 0 · Weeks 1–2 · Aug 31 – Sep 13 — Instrument

| Item | Detail |
|---|---|
| **Build** | Agent SDK Fluency **Ch6 (Evals)** via `CHAPTER_PLAYBOOK.md` Phases A→D. Sources: `evals-agent-performance/` + `tdd-for-agents/` |
| **Spendly** | Golden dataset over the intent classifier — the 5 test cases due since 2026-06-12 |
| **Remediation** | **Git**, 20 min/day: branch · merge · rebase · interactive rebase · conflict resolution · reset vs revert · stash · clean PR. Practised on `agentic-ai-from-scratch` itself. **No AI.** |
| **Teaching** | Ch0 (Python for Agents) · Ch1 (The Agent Loop) |
| **Also** | Build the PRIMM class template (§6.2). Archive `roles-this-book-trains` locally |
| **Proof** | Ch6 built · golden dataset green · **5 real branches + PRs authored by hand** |

### Phase 1 · Weeks 3–6 · Sep 14 – Oct 11 — BUILD

| Item | Detail |
|---|---|
| **Source** | `chapter-34-openai-agents-sdk/Openai Agents Sdk.md` — L4 Handoffs → L5 Guardrails → L6 Sessions → L7 Tracing/Hooks → L8 MCP consumer → L9 RAG FileSearchTool → L10 Capstone |
| **Currency** | **C32**, read once (90 min) as a delta list. Organising claim worth keeping: *"every agent bug is either a state bug or a trust bug"* |
| **Spendly** | `handoff()` Expense ↔ Insights · card-number **input** guardrail + cross-user-leak **output** guardrail + **`@tool_input_guardrail`** · `SQLiteSession` keyed by `user_phone` · `RunHooks` JSON logging · **`needs_approval=True`** on delete/export · run compaction |
| **Note** | `SandboxAgent` exists — know it, don't build it yet |
| **Teaching** | Ch2 (Typed Tools) · Ch3 (Structured Outputs) · Ch4 (Sessions & State) |
| **Proof** | **Capstone passes its own validation checklist** (PII block, refund routing, RAG citation). All mechanisms visibly in Spendly |

> This phase has been an open loop since 2026-06-13. It is four weeks of work.

### Phase 2 · Weeks 7–11 · Oct 12 – Nov 15 — CONNECT + SERVE

| Item | Detail |
|---|---|
| **Source** | `mcp-fundamentals/` → `custom-mcp-servers/` → **`fastapi-for-agents/`** (archive — the only copy, and better) |
| **Currency** | **C28** (pgvector RAG on Postgres) + **C33** (five-table Worker schema: `conversations`, `documents`, `embeddings`, `audit_log`, `capability_invocations`; audit trail as closed-vocabulary ledger; MCP for the build plane vs function tools for the runtime) |
| **Remediation** | **SQL**, 20 min/day, on Spendly's real schema: design · normalise · index deliberately · `EXPLAIN` every slow query · migrations. Backed by `relational-databases-sqlmodel/` |
| **Spendly** | Published MCP server exposing `query_expenses` / `get_insights` · aiosqlite → **Postgres + pgvector** via SQLModel with migrations · **off ngrok, onto real hosting** |
| **Teaching** | Ch5 (Context Window) · Ch6 (Evals) |
| **Proof** | An MCP server a stranger can connect to · Spendly at a URL that survives a reboot · **a schema you can defend under questioning** |

### Phase 3 · Weeks 12–16 · Nov 16 – Dec 20 — PROVE

| Item | Detail |
|---|---|
| **Source** | `evals-agent-performance/` (11 sections) → `tdd-for-agents/` → `multi-agent-reliability.md` |
| **Currency** | **C40** — nine-layer pyramid as the coverage checklist: *unit → integration → output → tool-use → trace → RAG → safety → regression → production*. Toolchain: **DeepEval** (CI gate) · **Ragas** (RAG) · **OpenAI Agent Evals** (trace) · **Phoenix** (production). Its Advanced-track CI gate **is** benchmark P5 |
| **Spendly** | Golden dataset ≥50 real cases · LLM-as-judge on insight quality · regression suite in CI · confidence thresholds + escalation paths |
| **Teaching** | **Cohort Core track graduates ~Week 16.** Past here, students read archive slugs through the PRIMM template. You author nothing |
| **Proof** | **A deliberately degraded prompt gets caught by CI, not by you** |

### Phase 4 · Weeks 17–22 · Dec 21 – Jan 31 — DEPLOY

| Item | Detail |
|---|---|
| **Source order** | `docker-for-ai-services/` → `observability-cost-engineering/` → `production-security/` → `cicd-gitops-argocd/` → `event-driven-kafka/` *(last only if Spendly has a real async workload)* |
| **Currency** | **C41** Reader + Beginner tracks. Harness/sandbox split: *"The harness is the control plane you own and keep running. The sandbox is the execution plane you create, use once, and throw away."* Stack: FastAPI on Azure Container Apps · Neon Postgres · Cloudflare R2 · E2B sandbox · Application Insights + OpenTelemetry + Phoenix on a shared `run_id` |
| **Replaces** | Archive `real-cloud-deployment/` |
| **Spendly** | Containerised · deployed · observable · secured · **CI-gated by the Phase 3 evals** |
| **Teaching** | Specialist extension — handoffs, guardrails, observability from archive slugs via PRIMM |
| **Proof** | **A stranger runs Spendly from the README alone** |

### Phase 5 · Weeks 23–26 · Feb 1 – Feb 28 — PROVE PUBLICLY

| Item | Detail |
|---|---|
| **Read** | **C42** Reader track (2–3 h): five-question decision tree → sequential workflow / single agent + ReAct / planning + ReAct / reflection / multi-agent. The best interview-answer generator in the book |
| **Certify** | **CCA-F** — Claude Certified Architect, Foundations (Anthropic; proctored, 60 scenario-based questions). The one certification your materials actually name |
| **Portfolio** | Spendly + MCP server + capstone FTE. README, architecture diagram, 3-min demo each |
| **Publish** | Resume and LinkedIn rewritten against `roles-this-book-trains`. **YouTube: publish the recorded class sessions** — you already produce 6 hrs/week of content for a live audience; the only incremental cost is the upload |
| **Proof** | 3 deployed agents + 1 monetisable product, public |

**Week 26 ends 2027-02-28 — exactly on the Feb 2027 target. There is no slack.** Miss two sessions in a week → cut a Tier 2 item, never re-plan.

---

## 6. Operating shape

### 6.1 The daily 60–90 minutes

| Block | Time | Rule |
|---|---|---|
| Build | 50 min | Code only. No reading, no doc authoring, no planning |
| Remediation | 20 min | Git (Phases 0–1) then SQL (Phase 2+). Fixed slot, never skipped, **never AI-assisted** |
| Log | 10 min | `RUNS.md`: what ran, what broke, what changed. This is your eval trace |

### 6.2 The class template — one unit, reused for all 78 sessions

```
2-hour class unit (fixed forever)
├─ 0:00  Predict      — code on screen, students write expected output. No running. (15m)
├─ 0:15  Run          — run it. Score prediction vs reality. This is the assessment. (10m)
├─ 0:25  Investigate  — why the gap? Read the source, the docs, the traceback. (25m)
├─ 0:50  Make         — build the same mechanism in a NEW domain, blank file. (40m)
├─ 1:30  Modify       — break it on purpose, fix it, log what broke. (25m)
└─ 1:55  Log          — one paragraph into RUNS.md. Non-negotiable. (5m)
```

Prep per class: pick the code, write the answer key. **~20 minutes.** This is the largest single hour-recovery in the plan.

PRIMM's *Predict* step is also the validation instrument that was missing — for the students **and for you**. The gap between prediction and reality is a measured comprehension score, and it costs nothing to produce.

---

## 7. Explicit skip list — resist the urge

### 7.1 From the archive

| Slug | Why skipped | When to learn |
|---|---|---|
| `kubernetes-for-ai-services/` · `helm-charts/` · `dapr-core/` · `dapr-actors-workflows/` · `traffic-engineering/` · `cost-disaster-recovery/` | Not needed for one deployed Worker. **The live book declines to teach them too** | The week a client's stack demands it |
| `google-adk-reliable-agents/` | A third framework fragments a consolidating skill base | On demand — days, not weeks |
| `chatkit-server/` · `openai-apps-sdk/` · `knowledge-graphs-graphrag/` | Vendor plumbing · niche channel · deferrable | On demand |
| `vector-databases-rag-langchain/` | Superseded by C28 + C33 (pgvector) | Never |

### 7.2 From the live book

| Course | Why skipped |
|---|---|
| 34 · Nervous System (Inngest) | **Defer, don't discard.** Durable execution, memoization, `step.wait_for_event`, replay is real production knowledge and ports to Temporal/Restate/Dapr. Promote it the moment Spendly drops work under load |
| 35 · Human-Agent Teams | Its own words: *"You will write little code here. You will write operating documents… the way a manager writes them."* Eight governance documents, no code |
| 36 · Designing Agent Experiences | A design discipline. Revisit for the MCP Apps lab after Feb 2027 |
| 37 · Paperclip · 38 · Dynamic Workforce · 39 · Identic AI | All three self-describe as **governance, not engineering**. They train the *stretch* role (AI-Native Company Architect) — being the board of a company that does not exist yet |
| 43 · Payment-Enabled Agents | Prereq C42; monetises a product with no users. *(It does cover merchant checkout via ACP, not only machine-to-machine — revisit when Spendly has paying users)* |

### 7.3 Cut from Spendly's scope for these 26 weeks

| Item | Verdict |
|---|---|
| **Redis** | Postgres + proper indexes handle your load. Never taught in either archive |
| **Payment gateway** | Monetise after a user exists |
| **Mobile app** | **WhatsApp is the mobile app.** That was the whole design |

---

## 8. Proof of mastery — binary, dated, no partial credit

### Yours

| # | Benchmark | Due | Pass condition |
|---|---|---|---|
| P1 | **Cold build** | W16 & W26 | Blank file, unfamiliar domain, no scaffolding: working SDK agent with typed tools + session + guardrail + eval suite, **in 90 minutes** |
| P2 | **Git, unassisted** | W6 | Rebase a 3-commit branch onto a moved `main`, resolve a real conflict, open a clean PR. **Timed. No AI. Fail = repeat next week** |
| P3 | **SQL, unassisted** | W11 | Spendly's slowest query: add the right index, show `EXPLAIN` before and after, explain the plan change aloud |
| P4 | **MCP whiteboard** | W11 | Draw resources / tools / prompts / transports from memory, then open your own published server as the worked example |
| P5 | **The eval gate** | W16 | Deliberately degrade a prompt. **CI fails before you do** |
| P6 | **Cold-start deploy** | W22 | A stranger runs Spendly from the README alone |
| P7 | **Explain under pressure** | ongoing | Any concept you teach, explained live with no generated article in front of you |
| P8 | **The freeze holds** | W26 | Count of planning `.md` files at W26 ≤ count at W0. **One new strategy document is a failure of this plan regardless of what else shipped** |

### Your students'

| # | Benchmark | When | Pass condition |
|---|---|---|---|
| S1 | Prediction accuracy | every class | Predict-vs-actual logged per student. A rising trend means the teaching works |
| S2 | `RUNS.md` discipline | every chapter | 3 dated runs, real pasted output, one paragraph on what broke. **A broken agent with documented breakage passes; a working agent with no runs does not** |
| S3 | Cohort cold build | W16 | ≥70% produce a working tool-using agent in a new domain, unaided, at reduced scope |
| S4 | Not-an-expense-tracker | W16 | Every student's Track 3 agent is in their own domain |

---

## 9. Standing rules

1. **Artifact or it didn't happen.** Every session ends with running code, a passing test, or a published thing.
2. **Spendly is the spine.** Every phase lands a Spendly milestone. There is no second project.
3. **One framework deeply before two shallowly.** Claude API / Agents Kit starts only after the Phase 1 capstone passes its checklist.
4. **LinkedIn post per completed lesson.** The public forcing function.
5. **Tests started in Phase 0**, not Phase 3.
6. **No new strategy documents.** This file is the last one. Amend it in place; never fork it.
7. **Authoring stops at Ch6.** Ch7–12 of Agent SDK Fluency are never built. Students past Ch6 read archive slugs through the PRIMM template. *(Resolve the 12→6 vs Ch0–6 contradiction between `README.md` and the counselling notes in one edit — pick a number, fix both files.)*
8. **Curriculum audits are quarterly, timeboxed to one session, and only against slugs on the critical path.** The 2026-08 audit is done. **Next audit: November 2026. Not before.** The site will change again; that is not an event.

---

## 10. Open resource gaps

Unresolved. The method is substitution until a source is named.

```
[MISSING: Git resource. Zero Git coverage in either archive (grepped: no hits for rebase / branching
 strategy). Method = deliberate practice on your own repos, no AI assist.]

[MISSING: SQL depth. relational-databases-sqlmodel is ORM-level; no schema-design, indexing-strategy
 or query-plan material exists in any named source.]

[MISSING: the other ~11 Claude certifications. Only CCA-F is identified
 (claudecertifications.com/claude-certified-architect). The rest cannot be scheduled until listed.]

[MISSING: personal website / portfolio method. Named as a goal; no resource attached.]

[MISSING: Spendly's current architecture, written down. It is the portfolio centrepiece and has no
 spec or schema doc. Phase 2 should produce one as a side-effect of the Postgres migration.]
```

---

## 11. Next action

**Phase 0, Week 1 — Monday 2026-08-31.** Two things, in this order:

1. `git checkout -b ch6-evals` in `agentic-ai-from-scratch` — by hand, no AI. That is P2, rep #1.
2. `CHAPTER_PLAYBOOK.md` Phase A: write Ch6's spec into `CLAUDE.md` *before* any code.

**Entry ticket** (carried from v1, still unanswered): explain why Spendly's Intent Classifier → Expense Extractor is currently orchestration (agent-as-tool), and what would change *for the user* if it became a true `handoff()`.
