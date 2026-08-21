# InsightGenie

> An AI-powered Analytics Agent that enables users to explore business data through natural language by generating, validating and executing SQL queries with business semantics, observability and AI evaluation.

---

## Overview

Modern organizations accumulate large volumes of structured data, but extracting insights often requires SQL knowledge, understanding of database schemas and familiarity with business rules.

**InsightGenie** explores how Large Language Models (LLMs), semantic layers and agentic workflows can bridge this gap.

Users can ask analytical questions such as:

> *Which customer generated the highest revenue?*

> *Which region had the highest margin?*

> *How many customers were active in February?*

The agent interprets the question, applies business definitions, generates SQL, validates and executes the query, and returns a grounded answer in natural language.

The current version also introduces **observability and AI evaluation**, allowing the workflow to be traced and its quality measured.

---

# Problem Statement

Traditional Text-to-SQL solutions can understand database schemas but may lack knowledge about the actual meaning of business metrics.

For example, a database may contain:

```text
revenue
cost
volume
active
```

But an analytical agent also needs to understand concepts such as:

```text
Margin = Revenue - Cost

Positivation = Distinct active customers

Revenue = SUM(revenue)
```

A generated SQL query can therefore be syntactically correct while still being incorrect from a business perspective.

There is also another challenge: knowing whether an AI-generated analytical answer can actually be trusted.

InsightGenie addresses these problems by combining:

* Text-to-SQL
* Business Semantic Layer
* Deterministic normalization
* SQL guardrails
* LangGraph workflows
* Conditional routing
* Automatic error recovery
* Grounded answer generation
* LangWatch observability
* AI quality evaluation

---

# Current Version — V5

The current version introduces **Observability & Evaluation** on top of the V4 Business Semantic Layer.

The agent evolves from:

```text
Business-aware Analytics Agent
```

into an:

```text
Observable
Business-aware
Analytics Agent
```

The workflow can now be inspected through traces and spans while different evaluators measure the quality of generated SQL and final answers.

---

# Current Features

* Natural language analytical questions
* LLM-based Text-to-SQL
* DuckDB analytical database
* CSV data ingestion
* Business Semantic Layer
* Business metrics and dimensions
* Business rules and aliases
* Deterministic normalization
* LangGraph orchestration
* Shared agent state
* Conditional routing
* SQL safety validation
* Semantic SQL validation
* Automatic SQL regeneration
* Retry control
* Database error recovery
* Grounded natural-language answers
* LangWatch tracing
* Workflow spans
* Prompt and SQL tracing
* Model metadata
* Latency observability
* Retry and error tracking
* SQL validity evaluation
* Semantic SQL correctness evaluation
* Groundedness evaluation
* Hallucination evaluation

---

# Architecture

```text
                     User
                      │
                      ▼
              Natural Language
                  Question
                      │
                      ▼
           Load Semantic Context
                      │
                      ▼
          Normalize Business Terms
                      │
                      ▼
                Generate SQL
                      │
                      ▼
                Validate SQL
                      │
                 SQL valid?
                 /       \
               yes       no
                │         │
                ▼         ▼
       Semantic Evaluation
                │      Regenerate SQL
                │         ▲
                ▼         │
           Execute SQL ────┘
                │
                ▼
          Generate Answer
                │
                ▼
          Evaluate Answer
                │
                ▼
               END
```

Observability is applied across the workflow:

```text
                 LangWatch
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
      Traces      Metrics    Evaluations
        │           │           │
      Spans       Latency     SQL Validity
      Prompt      Retries     Semantic SQL
      SQL         Errors      Groundedness
      Result      Model       Hallucination
      Answer
```

---

# Semantic Layer

InsightGenie separates physical database structure from business meaning.

## Physical Layer

Example:

```text
customer_id
customer_name
region
month
volume
revenue
cost
active
```

## Business Layer

Example:

```text
Revenue
    ↓
SUM(revenue)

Margin
    ↓
SUM(revenue - cost)

Positivation
    ↓
COUNT(DISTINCT customer_id)
WHERE active = 1
```

The resulting flow becomes:

```text
Business Question
        ↓
Business Semantics
        ↓
Database Schema
        ↓
SQL
        ↓
Query Result
        ↓
Business Answer
```

---

# Deterministic Normalization

Known mappings should not depend entirely on LLM interpretation.

For example, the database may store:

```text
2026-01
2026-02
```

while the user asks:

```text
Quantos clientes foram positivados em fevereiro?
```

The normalization layer converts:

```text
fevereiro
    ↓
2026-02
```

before SQL generation.

This follows an important project principle:

> **Deterministic rules should remain deterministic. The LLM should focus on interpretation.**

---

# LangGraph Workflow

LangGraph orchestrates the analytical workflow through specialized nodes:

```text
load_semantic_context
        ↓
normalize_question
        ↓
generate_sql
        ↓
validate_sql
        ↓
evaluate_semantic_sql
        ↓
execute_sql
        ↓
generate_answer
        ↓
evaluate_answer
```

Conditional routing allows the workflow to recover from invalid SQL, semantic problems and database execution errors.

```text
                         ┌── execute
validate_sql ────────────┤
                         └── regenerate

                         ┌── execute
semantic_evaluation ─────┤
                         └── regenerate

                         ┌── answer
execute_sql ─────────────┤
                         └── regenerate
```

A retry counter prevents infinite correction loops.

---

# Observability with LangWatch

V5 introduces LangWatch to provide visibility into the agent execution lifecycle.

Each user interaction can be represented as a trace containing spans for important workflow operations.

Example:

```text
InsightGenie Query
│
├── Load Semantic Context
├── Normalize Question
├── Generate SQL
├── Validate SQL
├── Semantic SQL Evaluation
├── Execute SQL
├── Generate Answer
└── Answer Evaluation
```

This makes it possible to inspect how an answer was produced rather than observing only the final output.

The observability layer tracks information such as:

```text
Question
Normalized Question
Generated SQL
Query Result
Final Answer
Model
Latency
Retries
Errors
Evaluation Results
```

---

# AI Evaluation

V5 introduces four initial quality evaluations.

## SQL Validity

Checks whether generated SQL follows the allowed query rules.

Examples of blocked operations:

```text
INSERT
UPDATE
DELETE
DROP
ALTER
TRUNCATE
```

Analytical execution is restricted to read operations.

---

## Semantic SQL Correctness

Checks whether SQL respects known business definitions.

Example:

```text
Question:
Quantos clientes foram positivados em fevereiro?

Expected semantics:

positivation → active = 1
february    → 2026-02
```

A query such as:

```sql
WHERE active = 1
AND month = '2026-02'
```

passes the known semantic rules.

---

## Groundedness

Evaluates whether the final natural-language answer is supported by the SQL result.

Example:

```text
SQL Result:
positivated_customers = 3

Answer:
Em fevereiro, foram positivados 3 clientes.
```

The answer is grounded because its factual claim comes directly from the query result.

---

## Hallucination Detection

Checks whether the final answer introduces information that is not supported by the database result.

This separates two different quality problems:

```text
SQL correctness
       ≠
Answer groundedness
```

A response can faithfully reproduce the result of an incorrect SQL query. For this reason, InsightGenie evaluates both SQL semantics and final-answer quality.

---

# Example

Question:

```text
Quantos clientes foram positivados em fevereiro?
```

Normalized question:

```text
Quantos clientes foram positivados em 2026-02?
```

Generated SQL:

```sql
SELECT
    COUNT(DISTINCT customer_id)
        AS positivated_customers
FROM sales
WHERE active = 1
AND month = '2026-02';
```

Result:

```text
positivated_customers
3
```

Final answer:

```text
Em fevereiro, foram positivados 3 clientes.
```

Evaluations:

```text
SQL Validity
✓

Semantic SQL Correctness
✓

Groundedness
✓

Hallucination Free
✓
```

---

# Project Structure

```text
insightgenie/
│
├── data/
│   └── sales.csv
│
├── database/
│   ├── __init__.py
│   └── duckdb_client.py
│
├── agents/
│   ├── __init__.py
│   └── sql_agent.py
│
├── semantic/
│   ├── __init__.py
│   └── business_metrics.py
│
├── evaluators/
│   ├── __init__.py
│   ├── sql_validity.py
│   ├── semantic_sql.py
│   └── answer_quality.py
│
├── observability/
│   ├── __init__.py
│   └── langwatch_client.py
│
├── graph/
│   ├── __init__.py
│   ├── state.py
│   └── workflow.py
│
├── tests/
├── .env
├── .gitignore
├── pyproject.toml
├── README.md
└── main.py
```

---

# Technologies

### Core

* Python 3.12+
* uv
* DuckDB
* Pandas
* Pydantic

### AI

* OpenAI
* LangChain

### Agent Orchestration

* LangGraph
* StateGraph
* Conditional Edges
* Shared State
* Retry Workflows

### Semantic Layer

Custom Python definitions for:

* Business metrics
* Dimensions
* Aliases
* Business rules
* Deterministic mappings

### Observability & Evaluation

* LangWatch
* Traces
* Spans
* Custom Evaluators

### Planned Data Platform

* Databricks SQL
* SQL Warehouse
* Unity Catalog

---

# Installation

Clone the repository:

```bash
git clone https://github.com/your-user/insightgenie.git
cd insightgenie
```

Create the environment:

```bash
uv venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
uv sync
```

---

# Configuration

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_key
LANGWATCH_API_KEY=your_langwatch_api_key
```

Never commit API keys or secrets.

---

# Running

Execute:

```bash
uv run python main.py
```

Example:

```text
Pergunta:
Quantos clientes foram positivados em fevereiro?

SQL final:
SELECT COUNT(DISTINCT customer_id)
FROM sales
WHERE active = 1
AND month = '2026-02'

Tentativas de correção: 0

Resultado SQL:
3

InsightGenie:
Em fevereiro, foram positivados 3 clientes.
```

Use:

```text
sair
```

to terminate the application.

---

# Project Evolution

## V1 — Text-to-SQL

* Natural language questions
* SQL generation
* DuckDB
* CSV datasets
* Query execution

```text
Question → SQL → DuckDB → Result
```

## V2 — LangGraph

* StateGraph
* Shared state
* Workflow nodes
* Natural-language answers

## V3 — Conditional Workflow

* Conditional routing
* SQL validation
* Automatic retry
* SQL regeneration
* Database error recovery

## V4 — Business Semantic Layer

* Business metrics
* Business dimensions
* Business rules
* Aliases
* Deterministic normalization
* Semantic-aware Text-to-SQL

## V5 — Observability & Evaluation

**Current version**

* LangWatch integration
* Trace and span instrumentation
* Prompt and SQL tracing
* Model metadata
* Latency observability
* Retry/error tracking
* SQL validity evaluation
* Semantic SQL correctness
* Groundedness evaluation
* Hallucination detection

---

# Roadmap

## V6 — Databricks Integration

Planned:

* Databricks SQL
* SQL Warehouse
* Unity Catalog
* Remote query execution
* Controlled catalog access

## V7 — Advanced Evaluation

Planned:

* LLM-as-a-Judge expansion
* Evaluation datasets
* Regression testing
* Answer relevance
* Business-rule compliance
* Evaluation dashboards

## V8 — FinOps

Planned:

* Token consumption
* Cost per interaction
* Model cost analysis
* Latency analytics
* Usage dashboards

## V9 — Adoption Analytics

Planned:

* Users and sessions
* Acceptance rate
* Reformulations
* Abandonment
* Query patterns

## V10 — Governance

Planned:

* RBAC
* PII masking
* Audit logs
* Retention policies
* Sensitive data controls

---

# Design Principles

**Business semantics should be explicit.**
Metric definitions should not depend entirely on LLM interpretation.

**Deterministic rules should remain deterministic.**
Known mappings and validations should be handled by code whenever possible.

**Generated SQL should not automatically be trusted.**
Queries must pass validation before database execution.

**Answers should be grounded.**
Final answers must be supported by query results.

**Recovery should be controlled.**
Retries are limited to prevent infinite loops.

**AI systems should be observable.**
A production-oriented agent should expose how requests are processed, not only their final answers.

**AI quality should be measurable.**
SQL correctness and answer quality are evaluated separately.

---

# Learning Objectives

InsightGenie explores practical applications of:

* Agentic AI
* Text-to-SQL
* Semantic Layers
* Business-aware AI
* LangGraph
* Conditional routing
* Self-correcting agents
* SQL guardrails
* AI Observability
* LLM Evaluation
* Groundedness
* Hallucination Detection
* Enterprise Data Platforms
* LLM Governance
* Production AI Engineering

---

# Status

**Current:** `V5 — Observability & Evaluation`

**Next:** `V6 — Databricks Integration`

---

# License

This project is intended for educational, research and portfolio purposes.
