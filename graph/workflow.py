import os
from typing import Optional

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

from graph.state import AgentState
from agents.sql_agent import generate_sql
from database.duckdb_client import DatabaseClient

# Load local development credentials before any OpenAI client is created.
load_dotenv()

database = DatabaseClient()

database.load_data("data/sales.csv")

def generate_sql_node(state: AgentState):
    sql = generate_sql(
        question=state["question"],
        schema=state["schema"]
    )

    return {
        "sql": sql
    }

def validate_sql_node(state: AgentState):
    sql = state["sql"].strip().lower()

    forbidden_commands = [
        "delete",
        "drop",
        "update",
        "insert",
        "alter",
        "truncate"
    ]

    if not sql.startswith("select"):
        return {
            "error": "Only SELECT queries are allowed."
        }

    for command in forbidden_commands:
        if command in sql:
            return {
                "error": f"Forbidden SQL command detected: {command}"
            }

    return {
        "error": ""
    }

def execute_sql_node(state: AgentState):

    if state["error"]:
        return {}

    try:
        result = database.execute(
            state["sql"]
        )

        return {
            "query_result": result.to_string()
        }

    except Exception as e:
        return {
            "error": str(e)
        }


from langchain_openai import ChatOpenAI


_answer_llm: Optional[ChatOpenAI] = None


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


def generate_answer_node(state: AgentState):

    if state["error"]:
        return {
            "answer": f"Não foi possível responder: {state['error']}"
        }

    prompt = f"""
Answer the user's question using only the SQL result below.

Question:
{state["question"]}

SQL:
{state["sql"]}

SQL result:
{state["query_result"]}

Rules:
- Do not invent information.
- Base the answer only on the SQL result.
- Answer in Portuguese.
"""

    response = _get_answer_llm().invoke(prompt)

    return {
        "answer": response.content
    }

builder = StateGraph(AgentState)

builder.add_node(
    "generate_sql",
    generate_sql_node
)

builder.add_node(
    "validate_sql",
    validate_sql_node
)

builder.add_node(
    "execute_sql",
    execute_sql_node
)

builder.add_node(
    "generate_answer",
    generate_answer_node
)

builder.add_edge(
    START,
    "generate_sql"
)

builder.add_edge(
    "generate_sql",
    "validate_sql"
)

builder.add_edge(
    "validate_sql",
    "execute_sql"
)

builder.add_edge(
    "execute_sql",
    "generate_answer"
)

builder.add_edge(
    "generate_answer",
    END
)

graph = builder.compile()
