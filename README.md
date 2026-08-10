# InsightGenie

> An AI-powered Analytics Agent that enables users to explore business data through natural language while automatically generating and executing SQL queries.

---

## Overview

Modern organizations accumulate large volumes of structured data, but extracting insights from that data often depends on technical skills such as SQL, data modeling, and knowledge of the underlying database.

InsightGenie demonstrates how Large Language Models (LLMs) can bridge this gap by translating natural language questions into executable SQL queries, retrieving the requested information, and returning answers in plain language.

Instead of navigating dashboards or writing SQL manually, users can simply ask questions such as:

> *Which customer generated the highest revenue?*

or

> *What was the total revenue by region?*

The agent interprets the question, generates a valid SQL query, executes it against the database and summarizes the results.

---

# Problem Statement

Business users frequently depend on technical teams to answer analytical questions.

Typical challenges include:

- Limited SQL knowledge among business users
- Slow turnaround for ad-hoc analyses
- Difficulty understanding database schemas
- Risk of writing incorrect or inefficient SQL
- Lack of governance around AI-generated database queries

InsightGenie explores how AI agents can safely assist analytical workflows while maintaining control over query execution.

---

# Project Goals

This project has four main objectives:

- Translate natural language into SQL
- Execute analytical queries against structured datasets
- Produce grounded business answers based only on database results
- Evolve into an enterprise-grade AI Analytics Agent with observability, governance and evaluation capabilities

---

# Current Features (V1)

Current implementation includes:

- Natural language questions
- SQL generation using an LLM
- DuckDB in-memory database
- CSV data loading
- Automatic SQL execution
- Query results displayed in the terminal

Example:

```text
Question

↓

Generate SQL

↓

Execute SQL

↓

Return Results
```

---

# Planned Roadmap

## V1

- Text-to-SQL
- DuckDB
- CSV datasets

---

## V2

- LangGraph orchestration
- Workflow nodes
- State management

---

## V3

- Conditional routing
- SQL validation
- Automatic retry
- Error recovery

---

## V4

- Semantic Layer
- Business metrics
- SQL Guardrails

---

## V5

- Databricks integration
- SQL Warehouse
- Unity Catalog

---

## V6

- LangWatch tracing
- LLM Observability
- Prompt tracking
- Cost tracking

---

## V7

- AI Evaluators
- Grounding
- Hallucination detection
- SQL correctness

---

## V8

- FinOps dashboards
- Token consumption
- Latency metrics
- Cost analytics

---

## V9

- User adoption metrics
- Acceptance rate
- Query analytics

---

## V10

- Governance
- RBAC
- PII masking
- Audit logs
- Retention policies

---

# Architecture (V1)

```
                 User

                   │

                   ▼

            SQL Generation

                   │

                   ▼

               DuckDB

                   │

                   ▼

          Query Execution

                   │

                   ▼

             Query Results
```

---

# Technologies

## Core

- Python 3.12+
- uv
- DuckDB
- Pandas

## AI

- OpenAI
- LangChain
- Pydantic

## Agent Framework

- LangGraph *(planned)*

## Observability *(planned)*

- LangWatch

## Data Platform *(planned)*

- Databricks SQL
- Unity Catalog

---

# Project Structure

```
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
├── graph/
│   └── ...
│
├── tests/
│
├── .env
├── pyproject.toml
└── main.py
```

---

# Installation

Clone the repository:

```bash
git clone https://github.com/your-user/insightgenie.git

cd insightgenie
```

Create the virtual environment:

```bash
uv venv
```

Activate it.

Windows

```powershell
.venv\Scripts\activate
```

Linux / macOS

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

---

# Running the Project

Execute:

```bash
uv run python main.py
```

---

# Example

Question:

```
Which customer generated the highest revenue?
```

Generated SQL

```sql
SELECT
    customer_name,
    SUM(revenue) AS total_revenue
FROM sales
GROUP BY customer_name
ORDER BY total_revenue DESC
LIMIT 1;
```

Output

```text
customer_name    total_revenue

Customer A       283000
```

---

# Future Vision

InsightGenie is designed as an educational and experimental project that gradually evolves from a simple Text-to-SQL application into a production-style AI Analytics Agent.

The long-term architecture will include:

- Multi-step AI workflows
- Autonomous SQL correction
- Enterprise observability
- AI quality evaluation
- Governance and compliance
- Cost monitoring
- Secure database access
- Business semantic layer
- Production-ready deployment

---

# Learning Objectives

This repository explores practical applications of:

- Agentic AI
- Text-to-SQL
- LangGraph workflows
- Prompt Engineering
- AI Observability
- AI Evaluation
- Enterprise Data Platforms
- LLM Governance
- Production AI Engineering

---

# License

This project is intended for educational, research and portfolio purposes.