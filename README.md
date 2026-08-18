# InsightGenie

> An AI-powered Analytics Agent that enables users to explore business data through natural language by generating, validating and executing SQL queries using a business-aware semantic layer.

---

## Overview

Modern organizations accumulate large volumes of structured data, but extracting insights often requires SQL knowledge, understanding of database schemas and familiarity with business rules.

**InsightGenie** explores how Large Language Models (LLMs) and agentic workflows can bridge this gap.

Users can ask questions such as:

> *Which customer generated the highest revenue?*

> *Which region had the highest margin?*

> *How many customers were active in February?*

The agent interprets the question, applies business definitions, generates SQL, validates and executes the query, and finally returns a grounded answer in natural language.

---

## Problem Statement

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

Without this semantic knowledge, an LLM may generate SQL that is syntactically valid but incorrect from a business perspective.

InsightGenie addresses this problem by combining:

* Text-to-SQL
* Business Semantic Layer
* Deterministic normalization
* SQL guardrails
* LangGraph workflows
* Conditional routing
* Automatic error recovery
* Grounded answer generation

---

# Current Version — V4

The current version introduces a **Business Semantic Layer**.

The agent evolves from a:

```text
Schema-aware Agent
```

into a:

```text
Business-aware Analytics Agent
```

It understands both the physical database schema and explicit definitions of business metrics, dimensions and rules.

---

## Current Features

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
* Automatic SQL regeneration
* Retry control
* Database error recovery
* Grounded natural-language answers

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
          Execute SQL   Regenerate SQL
                │         │
                │         └──────────┐
                ▼                    │
          Execution OK?              │
             /      \                 │
           yes      no ───────────────┘
            │
            ▼
       Generate Answer
            │
            ▼
           END
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

Margin Percentage
    ↓
(SUM(revenue) - SUM(cost))
/ SUM(revenue) * 100

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
How many customers were active in February?
```

The normalization layer can translate:

```text
February
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
execute_sql
        ↓
generate_answer
```

Conditional routing allows the agent to recover from problems.

```text
                 ┌──→ execute_sql
validate_sql ────┤
                 └──→ regenerate_sql
```

Database execution errors can also trigger SQL regeneration.

A retry counter prevents infinite loops.

---

# SQL Safety

Generated SQL is validated before execution.

The current version is designed for analytical read operations and blocks commands such as:

```text
INSERT
UPDATE
DELETE
DROP
ALTER
TRUNCATE
```

Only `SELECT` queries should reach the database execution layer.

This creates a separation between:

```text
LLM SQL Generation
        ↓
SQL Validation
        ↓
Database Execution
```

---

# Example

Question:

```text
Qual cliente teve maior margem?
```

Semantic definition:

```text
Margin = SUM(revenue - cost)
```

Generated SQL:

```sql
SELECT
    customer_name,
    SUM(revenue - cost) AS total_margin
FROM sales
GROUP BY customer_name
ORDER BY total_margin DESC
LIMIT 1;
```

The query is validated, executed against DuckDB and the result is converted into a natural-language answer.

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

### Planned

* LangWatch
* Databricks SQL
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
Pergunta: Qual cliente teve maior margem?

SQL final:
SELECT ...

Tentativas de correção: 0

Resultado SQL:
...

InsightGenie:
...
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
* CSV dataset
* SQL execution

```text
Question → SQL → DuckDB → Result
```

## V2 — LangGraph

* StateGraph
* Shared state
* Workflow nodes
* Natural-language answers

```text
generate_sql
     ↓
validate_sql
     ↓
execute_sql
     ↓
generate_answer
```

## V3 — Conditional Workflow

* Conditional routing
* SQL validation
* Automatic retry
* SQL regeneration
* Database error recovery

```text
             ┌── execute
validate ────┤
             └── regenerate
```

## V4 — Semantic Layer

**Current version**

* Business metrics
* Business dimensions
* Business rules
* Metric aliases
* Deterministic normalization
* Semantic-aware Text-to-SQL
* SQL guardrails
* Conditional recovery

```text
Natural Language
       +
Business Semantics
       +
Text-to-SQL
       +
SQL Safety
       +
Conditional Recovery
```

---

# Roadmap

## V5 — Observability & Evaluation

Planned:

* LangWatch integration
* Trace IDs
* Prompt and SQL tracing
* Latency
* Token usage
* Model metadata
* Retry/error tracking

Initial evaluators:

* SQL validity
* Semantic SQL correctness
* Groundedness
* Hallucination detection

## V6 — Databricks

Planned:

* Databricks SQL
* SQL Warehouse
* Unity Catalog
* Remote query execution
* Controlled data access

## V7 — Advanced Evaluation

Planned:

* LLM-as-a-Judge
* Grounding score
* Hallucination score
* Answer relevance
* Business-rule compliance

## V8 — FinOps

Planned:

* Token consumption
* Cost per interaction
* Model costs
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
Final answers must be based on query results.

**Recovery should be controlled.**
Retries are limited to prevent infinite agent loops.

**Observability should be part of the architecture.**
Tracing, evaluation and cost monitoring are planned as first-class capabilities.

---

# Learning Objectives

InsightGenie explores:

* Agentic AI
* Text-to-SQL
* Semantic Layers
* Business-aware AI
* LangGraph
* Conditional routing
* Self-correcting agents
* SQL guardrails
* Prompt Engineering
* AI Observability
* AI Evaluation
* Enterprise Data Platforms
* LLM Governance

---

# Status

**Current:** `V4 — Business Semantic Layer`

**Next:** `V5 — Observability & Evaluation with LangWatch`

---

# License

This project is intended for educational, research and portfolio purposes.
