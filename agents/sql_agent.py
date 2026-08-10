import os
from typing import Optional

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


load_dotenv()


class SQLResponse(BaseModel):
    sql: str = Field(
        description="SQL query generated from the user question"
    )


# Lazily-created structured LLM. This avoids instantiating the OpenAI client
# at import-time (which previously caused an error when credentials were
# missing). Use `_get_structured_llm()` inside runtime paths so missing
# credentials are reported only when the LLM is actually needed.
_structured_llm: Optional[object] = None


def _get_structured_llm():
    global _structured_llm
    if _structured_llm is not None:
        return _structured_llm

    # Require at least one well-known OpenAI env var to be present.
    if not (os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_ADMIN_KEY")):
        raise RuntimeError(
            "Missing OpenAI credentials. Set the OPENAI_API_KEY or OPENAI_ADMIN_KEY environment variable, "
            "or pass credentials to the client."
        )

    llm = ChatOpenAI(
        model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0,
    )
    _structured_llm = llm.with_structured_output(SQLResponse)
    return _structured_llm


def generate_sql(question: str, schema: str) -> str:
    prompt = f"""
You are a SQL analyst.

Database schema:

{schema}

Table:
sales

Generate DuckDB SQL that answers the question.

Rules:
- Only SELECT queries are allowed.
- Never modify data.
- Use only columns present in the schema.

Question:
{question}
"""

    structured_llm = _get_structured_llm()
    response = structured_llm.invoke(prompt)
    return response.sql
