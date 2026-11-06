# Original Draft (Verbatim Notes)

# Introduction
I have decided to create a series dedicated to the topic of Agentic Governance and help others to bring all different puzles of a piece into a single structured picture. To understrand on the top level what kind of threads are possible, which guardrails can prevent them and how to look at the whole picture from the top level. This series are not meant to provide a bullet proof safe guarantee solution, but are meant to serve as some foundational level to understand the existing and known problems and is aimed to help bring it all together ina  coherent view. 

I have not found enough good materials on Agentic Governance presented in an easy to comprtehend and follow way, so I decided to start compilingit myself and will be sharing my notes as I go over the different topics. 

The first task I want to look into today is connecting an AI agent to the internal customer database and dive deep into what type of threads we need to be designing against and how each of them might be happening. 

Let's imagine we have a customer database and we want an AI agent to assist user in answering information using that data. For example, a user asking question abouts its order status. 

Let's design the architecture botton up.

Lets draw the initial diagram: 

---

# Part 01 · Designing the Connection

## Introduction: Connecting an AI Agent to an Internal Customer Database

I decided to start a series dedicated to **Agentic Governance** to help engineers and architects fit all the scattered pieces of this puzzle into a single, structured picture. My goal is to make it clear at the top level what kinds of **threats** are possible when we connect AI agents to real systems, which **guardrails** prevent them, and how all of those controls fit together end-to-end.

This series is not meant to promise a silver-bullet, 100% foolproof security guarantee—no architecture can. Instead, it is meant to serve as a practical foundation: walking through the known failure modes of agentic systems and bringing the architectural defenses together into one coherent mental model.

When I began researching Agentic Governance, I struggled to find material that explained the end-to-end mechanics in a clear, approachable way. So I started compiling my own architectural notes and diagrams, and I will be sharing them across this series as I work through each topic.

### Connecting an AI Agent to an Internal Customer Database

The first scenario we will look into today is one of the most common enterprise tasks: **connecting an AI agent to an internal customer database**, and diving deep into what types of threats we must design against and how each one happens in practice.

> **The Scenario:** Imagine we have an internal customer database (`customers` and `orders`) and we want an AI agent to assist users by answering questions from that data—for example, a customer asking: *"What is the current status of my order #104?"*

Let's design the architecture **bottom-up**. Let's draw the initial diagram:
- See [01_draft.html](file:///usr/local/google/home/evekhm/projects/fde-workspace/agentic-governance/01_draft.html) (and [01_draft.pdf](file:///usr/local/google/home/evekhm/projects/fde-workspace/agentic-governance/01_draft.pdf)).

---

# Part 02 · Examining the Initial Diagram

## Where Do the Threats Come From?

Nothing in Figure 1 is wrong as a functional design. The problem is that each of the three components makes an implicit trust assumption, and each of the four arrows carries data that nobody has checked. Figure 2 in [01_draft.html](file:///usr/local/google/home/evekhm/projects/fde-workspace/agentic-governance/01_draft.html) keeps the three components exactly as drawn and places each threat (`T1`–`T8`) where it strikes, with a one-line example. Below the threats are the seven design questions they raise:

| # | Question | What it asks |
| :--- | :--- | :--- |
| `Q1` (T3, T4) | Identity | How is the caller's identity verified and carried to the database — instead of being stated in the prompt or a tool argument? |
| `Q2` (T1) | Tool Boundary | How do we prevent the model from composing and executing its own SQL (`SELECT *`, `UNION`, `DROP`), rather than calling fixed tools? |
| `Q3` (T2, T3) | Row & Column Access | Even with a verified identity, how does the database itself return only Alice's rows (Row-Level Security) and hide PII columns (Column-Level Security)? |
| `Q4` (T2) | Poisoned Data | What if a row the agent reads — or previously wrote — contains hidden instructions or raw PII that then enters the model's context? |
| `Q5` (T7) | Writes & Approval | How is a write (refund, cancel, update) confirmed by a human before it executes, and protected from running twice on a retry? |
| `Q6` (T13) | Volume & Cost | What caps the number of rows returned, bytes scanned, and requests a single conversation can trigger against the database? |
| `Q7` (T6, T8) | Network & Audit | How do we prevent data from leaving the network, and attribute every query to a user and an agent turn after the fact? |

### Why Q3 Deserves Its Own Question

Q1 and Q3 are easy to conflate, but they are different layers of the problem. Q1 asks how the system establishes *who* is making the request and carries that fact to the database without trusting the prompt. Q3 asks what the database does with that identity once it arrives: even a correctly identified user must receive only the rows and columns they are entitled to see.

**Row-Level Security (RLS)** is a filter the database engine applies to every query on a table, regardless of how the query was written. If Alice's identity is bound to the connection, a query for `SELECT * FROM orders` returns only Alice's orders—even if the model omitted the `WHERE` clause, even if the tool was called with the wrong argument, and even if the prompt was injected. The filter lives in the database, not in the agent's code, so a fooled model cannot remove it.

**Column-Level Security (CLS)** is the same idea applied to columns. The `customers` table holds email addresses, physical addresses, payment details, and national identifiers in the same row as the fields the agent needs. CLS ensures that the agent's database identity either cannot read those columns at all or receives a masked value (for example, the last four digits of a card number), so raw PII never enters the model's context window or its logs.

Both controls are needed because the naive design violates both at once: the agent connects with one shared administrative account (so the database cannot distinguish Alice from Bob and RLS has nothing to filter on), and that account can read every column (so CLS is never applied). Answering Q3 therefore depends on answering Q1 first—the database can only enforce per-user access if it knows which user is asking. How this identity binding works differs between a data warehouse and a transactional database, and we cover both in detail in the Row and Column Access Controls section of the full blueprint.

---

# Structure from here on (see ep01_securing_agent_to_database.html)

The post is now `ep01_securing_agent_to_database.html`. Chapter 0 holds the introduction above plus the hero image (the governed GCP architecture, simplified from the reference map). Chapter 1 = Figure 1, Chapter 2 = Figure 2 + the Q3 explainer. From Chapter 3 each chapter adds one box using five beats: *Where we are* (growing diagram) → *What breaks without it* (one scenario) → *What it is* (platform-agnostic, then the GCP product) → *Closes / Still open* → *Go deeper* (one `ref/` link) → one-line transition.

| Chapter | New box | Closes | Deep-dive page |
| :-- | :-- | :-- | :-- |
| 3 · Take the SQL away from the model | Tool server: Google-managed remote MCP (`execute_sql` / `execute_sql_readonly`, model still writes SQL — [docs](https://docs.cloud.google.com/sql/docs/sqlserver/secure-agent-interactions-mcp)) vs [MCP Toolbox](https://github.com/googleapis/mcp-toolbox) on Cloud Run (fixed statements) | T1 T4 T13 | `ref/mcp-tool-server-options.html` (done) |
| 4 · Give the agent an identity | Agent Identity (SPIFFE) | T3 (credential half), prepares T5 | `ref/mtls-and-tokens.html` (todo) |
| 5 · Let the database decide | RLS / CLS / stored-proc writes — Stateless HTTP (BigQuery `useClientOAuth: true`, `SESSION_USER()`, `SECURE_CONTEXT()`, Dataplex policy tags) vs. Stateful Pooled TCP (Cloud SQL / AlloyDB shared pool role + MCP Toolbox `bound_params`/`authServices`, Cloud SQL Parameterized Secure Views `@local_customer_id` / `cloudsql.enable_parameterized_views`, and PostgreSQL `set_config(..., true)` + `FORCE RLS`) | T3 T2 (PII) T7 | `ref/rls-cls.html` (done) |
| 6 · Prove who is calling on every hop | `Corporate sign-in` · `Who is calling (mTLS + DPoP)` · `Auth Manager` (`RFC 8693` OBO Token Exchange `T1 → T2` & KMS Context JWTs) | T5 · T4 | `ref/mtls-and-tokens.html` (done) |
| 7 · Proxy in front (ingress) | `Ingress gateway` (`Who may invoke`, `Quotas`) · `Events & schedules` (Envoy reverse proxy) | T13, forged webhook | `ref/envoy-proxy.html` (done) |
| 8 · Proxy behind (egress) | `Egress gateway` (`default deny`, `May it call this: IAP`) · `Agent Registry` · `Gemini on Vertex AI` + Cloud Run 3-container `agent`+`envoy`+`tokenx` sidecar | T6 (part), T10, ASI04/10 | `ref/envoy-proxy.html` (done) |
| 9 · Screen in and out | `Model Armor` at Ingress & Egress + ADK `after_tool_callback` `normalize()` (NFKC, zero-width, Base64, fail-closed) + Cloud SDP surrogate tokens | T1/T2 mitigation + PII | `ref/model-armor.html` (done) |
| 10 · Close the network | `YOUR VPC` · `DATA TIER` · `PSC interface (10.10.9.2)` · `PSC endpoint & DNS (*.run.app · *.googleapis.com)` + 3 PSC Doors | T6 (network path) | `ref/psc-and-vpc-sc.html` (done) |
| 11 · Draw the perimeter | `VPC SERVICE CONTROLS PERIMETER · DATA PROJECT` + cross-project VPC-SC Ingress Policy | T6 (credential leak) | `ref/psc-and-vpc-sc.html` (done) |
| 12 · Keep the human in the loop | `Workflow graph` (`gemini-3.8-flash`, `mode="single_turn"`, `RequestInput` HITL gate rendering server-bound params) · `Memory Bank` · `Code sandbox` | T7, T9, ASI05/06/09 | — |
| 13 · See it and stop it | `Audit Logs · Trace · SCC` (W3C `traceparent`, 400-day Data Access BQ sink, `BigQueryAgentAnalyticsPlugin`) · `CONTROL PLANE` (`IAM allow, deny, PAB`, `Org Policy`, `Evaluation and red team`, `Kill switch`) | T8, ASI10 | `ref/audit-and-containment.html` (done) |
| 14 · The finished picture | 5-Hop Side-by-Side Comparison (`Flawed` vs `Governed`), `G1`–`G8` Summary Table, 22-Row OWASP Top 10 Matrix (`ASI01`–`ASI10` + `LLM01`–`LLM10`), and Official Google Cloud Blueprints | All 8 threats (`T1`–`T8`) | `ref/owasp-mapping.html` (done) |
