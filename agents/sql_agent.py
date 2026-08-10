import os
from typing import Optional

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


class SQLResponse(BaseModel):
    sql: str = Field(
        description="SQL query generated from the user question"
    )


load_dotenv()

_structured_llm: Optional[object] = None


def _get_structured_llm():
    global _structured_llm
    if _structured_llm is not None:
        return _structured_llm

    if not (os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_ADMIN_KEY")):
        raise RuntimeError(
            "Missing OpenAI credentials. Add OPENAI_API_KEY to .env or set it "
            "in the environment."
        )

    llm = ChatOpenAI(
        model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0,
    )
    _structured_llm = llm.with_structured_output(SQLResponse)
    return _structured_llm


def generate_sql(
    question: str,
    schema: str,
    previous_sql: str = "",
    error: str = ""
) -> str:

    correction_context = ""

    if previous_sql:
        correction_context = f"""
Previous SQL:

{previous_sql}

Problem detected:

{error}

Generate a corrected SQL query.
"""

    prompt = f"""
You are an expert DuckDB SQL analyst.

Database schema:

{schema}

Available table:

sales

User question:

{question}

{correction_context}

Rules:

- Generate only SELECT queries.
- Never use INSERT, UPDATE, DELETE, DROP, ALTER or TRUNCATE.
- Use only columns present in the schema.
- Use only the sales table.
- Return a valid DuckDB SQL query.
"""

    response = _get_structured_llm().invoke(prompt)

    return response.sql
