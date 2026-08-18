import os
from typing import Optional

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from agents.sql_agent import generate_sql
from database.duckdb_client import DatabaseClient
from graph.state import AgentState

from semantic.business_metrics import get_semantic_context


load_dotenv()

database = DatabaseClient()
database.load_data("data/sales.csv")

_answer_llm: Optional[ChatOpenAI] = None

def load_semantic_context_node(state: AgentState):

    semantic_context = get_semantic_context()

    return {
        "semantic_context": semantic_context
    }


def _get_answer_llm() -> ChatOpenAI:
    global _answer_llm
    if _answer_llm is not None:
        return _answer_llm

    if not (os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_ADMIN_KEY")):
        raise RuntimeError(
            "Missing OpenAI credentials. Add OPENAI_API_KEY to .env or set it "
            "in the environment."
        )

    _answer_llm = ChatOpenAI(
        model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0,
    )
    return _answer_llm


def generate_sql_node(state: AgentState):

    sql = generate_sql(
        question=state["question"],
        schema=state["schema"],
        semantic_context=state["semantic_context"],
    )

    return {
        "sql": sql,
        "error": "",
    }


def validate_sql_node(state: AgentState):
    sql = state["sql"].strip().lower()
    forbidden_commands = [
        "delete",
        "drop",
        "update",
        "insert",
        "alter",
        "truncate",
    ]

    if not sql.startswith("select"):
        return {"error": "Only SELECT queries are allowed."}

    for command in forbidden_commands:
        if command in sql:
            return {"error": f"Forbidden SQL command detected: {command}"}

    return {"error": ""}


def route_after_validation(state: AgentState):
    if state["error"]:
        if state["retry_count"] >= 2:
            return "failed"
        return "retry"
    return "execute"


def regenerate_sql_node(state: AgentState):

    sql = generate_sql(
        question=state["question"],
        schema=state["schema"],
        semantic_context=state["semantic_context"],
        previous_sql=state["sql"],
        error=state["error"],
    )

    return {
        "sql": sql,
        "error": "",
        "retry_count": state["retry_count"] + 1,
    }


def execute_sql_node(state: AgentState):
    try:
        result = database.execute(state["sql"])
        return {"query_result": result.to_string(), "error": ""}
    except Exception as exc:
        return {"error": str(exc)}


def route_after_execution(state: AgentState):
    if state["error"]:
        if state["retry_count"] >= 2:
            return "failed"
        return "retry"
    return "answer"


def generate_answer_node(state: AgentState):
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
    response = _get_answer_llm().invoke(prompt)
    return {"answer": response.content}


def failure_node(state: AgentState):
    return {
        "answer": (
            "Não consegui gerar uma consulta SQL válida "
            "após múltiplas tentativas."
        )
    }


builder = StateGraph(AgentState)
builder.add_node("load_semantic_context",load_semantic_context_node)
builder.add_node("generate_sql", generate_sql_node)
builder.add_node("validate_sql", validate_sql_node)
builder.add_node("regenerate_sql", regenerate_sql_node)
builder.add_node("execute_sql", execute_sql_node)
builder.add_node("generate_answer", generate_answer_node)
builder.add_node("failure", failure_node)

builder.add_edge(START,"load_semantic_context")
builder.add_edge("load_semantic_context","generate_sql")
builder.add_edge("generate_sql", "validate_sql")
builder.add_conditional_edges(
    "validate_sql",
    route_after_validation,
    {
        "execute": "execute_sql",
        "retry": "regenerate_sql",
        "failed": "failure",
    },
)
builder.add_edge("regenerate_sql", "validate_sql")
builder.add_conditional_edges(
    "execute_sql",
    route_after_execution,
    {
        "answer": "generate_answer",
        "retry": "regenerate_sql",
        "failed": "failure",
    },
)
builder.add_edge("generate_answer", END)
builder.add_edge("failure", END)

graph = builder.compile()
