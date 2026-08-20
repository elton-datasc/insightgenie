import os
from typing import Optional

import langwatch
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from agents.sql_agent import generate_sql
from database.duckdb_client import DatabaseClient
from evaluators.answer_quality import (
    evaluate_groundedness,
    evaluate_hallucination,
)
from evaluators.semantic_sql import evaluate_semantic_sql
from evaluators.sql_validity import evaluate_sql_validity
from graph.state import AgentState
from semantic.business_metrics import (
    get_semantic_context,
    normalize_business_terms,
)


load_dotenv()


# ============================================================
# CONFIG
# ============================================================

MODEL_NAME = "gpt-4o-mini"
MODEL_TEMPERATURE = 0
MAX_RETRIES = 2


# ============================================================
# DATABASE
# ============================================================

database = DatabaseClient()
database.load_data("data/sales.csv")


# ============================================================
# LLM
# ============================================================

_answer_llm: Optional[ChatOpenAI] = None


def _get_answer_llm() -> ChatOpenAI:
    global _answer_llm

    if _answer_llm is not None:
        return _answer_llm

    if not (
        os.environ.get("OPENAI_API_KEY")
        or os.environ.get("OPENAI_ADMIN_KEY")
    ):
        raise RuntimeError(
            "Missing OpenAI credentials. "
            "Add OPENAI_API_KEY to .env."
        )

    _answer_llm = ChatOpenAI(
        model=MODEL_NAME,
        temperature=MODEL_TEMPERATURE,
    )

    return _answer_llm


# ============================================================
# SEMANTIC CONTEXT
# ============================================================

@langwatch.span(name="Load Semantic Context")
def load_semantic_context_node(state: AgentState):

    semantic_context = get_semantic_context()

    return {
        "semantic_context": semantic_context,
    }


# ============================================================
# QUESTION NORMALIZATION
# ============================================================

@langwatch.span(name="Normalize Question")
def normalize_question_node(state: AgentState):

    normalized_question = normalize_business_terms(
        state["question"].lower()
    )

    span = langwatch.get_current_span()

    span.update(
        input={
            "question": state["question"],
        },
        output={
            "normalized_question": normalized_question,
        },
    )

    return {
        "normalized_question": normalized_question,
    }


# ============================================================
# SQL GENERATION
# ============================================================

@langwatch.span(name="Generate SQL")
def generate_sql_node(state: AgentState):

    span = langwatch.get_current_span()

    # Metadata deve conter apenas valores simples.
    span.update(
        metadata={
            "model": MODEL_NAME,
            "temperature": MODEL_TEMPERATURE,
            "operation": "text-to-sql",
        }
    )

    span.update(
        input={
            "question": state["question"],
            "normalized_question": state["normalized_question"],
            "semantic_context": state["semantic_context"],
        }
    )

    sql = generate_sql(
        question=state["normalized_question"],
        schema=state["schema"],
        semantic_context=state["semantic_context"],
    )

    span.update(
        output={
            "sql": sql,
        }
    )

    return {
        "sql": sql,
        "error": "",
    }


# ============================================================
# SQL VALIDATION
# ============================================================

@langwatch.span(
    name="Validate SQL",
    type="evaluation",
)
def validate_sql_node(state: AgentState):

    evaluation = evaluate_sql_validity(
        state["sql"]
    )

    span = langwatch.get_current_span()

    span.add_evaluation(
        name="sql_validity",
        passed=evaluation["passed"],
        score=evaluation["score"],
        details=evaluation["details"],
    )

    if not evaluation["passed"]:
        return {
            "error": evaluation["details"],
        }

    return {
        "error": "",
    }


def route_after_validation(state: AgentState):

    if state["error"]:

        if state["retry_count"] >= MAX_RETRIES:
            return "failed"

        return "retry"

    return "execute"


# ============================================================
# SEMANTIC SQL EVALUATION
# ============================================================

@langwatch.span(
    name="Semantic SQL Evaluation",
    type="evaluation",
)
def evaluate_semantic_sql_node(state: AgentState):

    evaluation = evaluate_semantic_sql(
        question=state["question"],
        sql=state["sql"],
    )

    span = langwatch.get_current_span()

    span.add_evaluation(
        name="semantic_sql_correctness",
        passed=evaluation["passed"],
        score=evaluation["score"],
        details=evaluation["details"],
    )

    if not evaluation["passed"]:
        return {
            "error": evaluation["details"],
        }

    return {
        "error": "",
    }


# ============================================================
# SQL REGENERATION
# ============================================================

@langwatch.span(name="Regenerate SQL")
def regenerate_sql_node(state: AgentState):

    next_retry = state["retry_count"] + 1

    span = langwatch.get_current_span()

    span.update(
        metadata={
            "model": MODEL_NAME,
            "temperature": MODEL_TEMPERATURE,
            "operation": "sql-regeneration",
            "retry_count": next_retry,
        }
    )

    span.update(
        input={
            "question": state["normalized_question"],
            "previous_sql": state["sql"],
            "error": state["error"],
        }
    )

    sql = generate_sql(
        question=state["normalized_question"],
        schema=state["schema"],
        semantic_context=state["semantic_context"],
        previous_sql=state["sql"],
        error=state["error"],
    )

    span.update(
        output={
            "sql": sql,
        }
    )

    return {
        "sql": sql,
        "error": "",
        "retry_count": next_retry,
    }


# ============================================================
# SQL EXECUTION
# ============================================================

@langwatch.span(name="Execute SQL")
def execute_sql_node(state: AgentState):

    span = langwatch.get_current_span()

    span.update(
        input={
            "sql": state["sql"],
        }
    )

    try:
        result = database.execute(
            state["sql"]
        )

        query_result = result.to_string()

        span.update(
            output={
                "result": query_result,
            }
        )

        return {
            "query_result": query_result,
            "error": "",
        }

    except Exception as exc:

        error_message = str(exc)

        span.update(
            output={
                "error": error_message,
            }
        )

        return {
            "error": error_message,
        }


def route_after_execution(state: AgentState):

    if state["error"]:

        if state["retry_count"] >= MAX_RETRIES:
            return "failed"

        return "retry"

    return "answer"


# ============================================================
# ANSWER GENERATION
# ============================================================

@langwatch.span(name="Generate Answer")
def generate_answer_node(state: AgentState):

    span = langwatch.get_current_span()

    span.update(
        metadata={
            "model": MODEL_NAME,
            "temperature": MODEL_TEMPERATURE,
            "operation": "generate-answer",
        }
    )

    prompt = f"""
You are a business data analyst.

Answer the question using only the SQL result.

Question:
{state["question"]}

SQL:
{state["sql"]}

Result:
{state["query_result"]}

Rules:
- Answer in Portuguese.
- Do not invent information.
- Use only information present in the SQL result.
"""

    span.update(
        input={
            "question": state["question"],
            "sql": state["sql"],
            "query_result": state["query_result"],
        }
    )

    response = _get_answer_llm().invoke(
        prompt
    )

    answer = response.content

    span.update(
        output={
            "answer": answer,
        }
    )

    return {
        "answer": answer,
    }


# ============================================================
# ANSWER EVALUATION
# ============================================================

@langwatch.span(
    name="Answer Evaluation",
    type="evaluation",
)
def evaluate_answer_node(state: AgentState):

    span = langwatch.get_current_span()

    groundedness = evaluate_groundedness(
        question=state["question"],
        query_result=state["query_result"],
        answer=state["answer"],
    )

    span.add_evaluation(
        name="groundedness",
        passed=groundedness.passed,
        score=groundedness.score,
        details=groundedness.explanation,
    )

    hallucination = evaluate_hallucination(
        query_result=state["query_result"],
        answer=state["answer"],
    )

    span.add_evaluation(
        name="hallucination_free",
        passed=hallucination.passed,
        score=hallucination.score,
        details=hallucination.explanation,
    )

    return {}


# ============================================================
# FAILURE
# ============================================================

@langwatch.span(name="Failure")
def failure_node(state: AgentState):

    return {
        "answer": (
            "Não consegui gerar uma consulta SQL válida "
            "após múltiplas tentativas."
        )
    }


# ============================================================
# GRAPH
# ============================================================

builder = StateGraph(
    AgentState
)


# ------------------------------------------------------------
# Nodes
# ------------------------------------------------------------

builder.add_node(
    "load_semantic_context",
    load_semantic_context_node,
)

builder.add_node(
    "normalize_question",
    normalize_question_node,
)

builder.add_node(
    "generate_sql",
    generate_sql_node,
)

builder.add_node(
    "validate_sql",
    validate_sql_node,
)

builder.add_node(
    "evaluate_semantic_sql",
    evaluate_semantic_sql_node,
)

builder.add_node(
    "regenerate_sql",
    regenerate_sql_node,
)

builder.add_node(
    "execute_sql",
    execute_sql_node,
)

builder.add_node(
    "generate_answer",
    generate_answer_node,
)

builder.add_node(
    "evaluate_answer",
    evaluate_answer_node,
)

builder.add_node(
    "failure",
    failure_node,
)


# ============================================================
# MAIN FLOW
# ============================================================

builder.add_edge(
    START,
    "load_semantic_context",
)

builder.add_edge(
    "load_semantic_context",
    "normalize_question",
)

builder.add_edge(
    "normalize_question",
    "generate_sql",
)

builder.add_edge(
    "generate_sql",
    "validate_sql",
)


# ============================================================
# SQL VALIDITY ROUTING
# ============================================================

builder.add_conditional_edges(
    "validate_sql",
    route_after_validation,
    {
        "execute": "evaluate_semantic_sql",
        "retry": "regenerate_sql",
        "failed": "failure",
    },
)


# ============================================================
# SEMANTIC SQL ROUTING
# ============================================================

builder.add_conditional_edges(
    "evaluate_semantic_sql",
    route_after_validation,
    {
        "execute": "execute_sql",
        "retry": "regenerate_sql",
        "failed": "failure",
    },
)


# ============================================================
# RETRY LOOP
# ============================================================

builder.add_edge(
    "regenerate_sql",
    "validate_sql",
)


# ============================================================
# SQL EXECUTION ROUTING
# ============================================================

builder.add_conditional_edges(
    "execute_sql",
    route_after_execution,
    {
        "answer": "generate_answer",
        "retry": "regenerate_sql",
        "failed": "failure",
    },
)


# ============================================================
# ANSWER + EVALUATION
# ============================================================

builder.add_edge(
    "generate_answer",
    "evaluate_answer",
)

builder.add_edge(
    "evaluate_answer",
    END,
)


# ============================================================
# FAILURE
# ============================================================

builder.add_edge(
    "failure",
    END,
)


graph = builder.compile()