import os
from pathlib import Path

from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

try:
    from dotenv import load_dotenv
except Exception:
    load_dotenv = None


class SQLResponse(BaseModel):
    sql: str = Field(
        description="SQL query generated from the user question"
    )


def _get_structured_llm() -> any:
    """Create and return a structured LLM instance.

    This function reads `OPENAI_API_KEY` from the environment. Callers may
    set the environment variable themselves (or pass an `api_key` to
    `generate_sql`, which will set it temporarily).
    """
    # Attempt to load from a .env file if the key is not already present.
    if "OPENAI_API_KEY" not in os.environ:
        if load_dotenv is not None:
            # Prefer a .env in repo root
            env_path = Path(__file__).resolve().parents[1] / ".env"
            load_dotenv(env_path)

    if "OPENAI_API_KEY" not in os.environ:
        raise RuntimeError(
            "Missing OpenAI API key. Set the OPENAI_API_KEY environment variable "
            "or call generate_sql(..., api_key=...) to provide one."
        )

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    return llm.with_structured_output(SQLResponse)


def generate_sql(question: str, schema: str, api_key: str = None) -> str:
    """Generate a DuckDB SQL query for the given question and schema.

    If `api_key` is provided, it will be set into `OPENAI_API_KEY` for this
    process (overwriting any existing value).
    """
    # If caller provided an API key, set it for this process.
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key

    structured_llm = _get_structured_llm()

    prompt = f"""
You are a SQL analyst.

Database:

{schema}

Table:
sales

Generate DuckDB SQL that answers the user question.

Rules:

- Return only a valid SQL query.
- Never modify data.
- Only SELECT queries are allowed.
- Use only columns present in the schema.

Question:

{question}
"""

    response = structured_llm.invoke(prompt)

    return response.sql