import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


load_dotenv()


class SQLResponse(BaseModel):
    sql: str = Field(
        description="SQL query generated from the user question"
    )


def _get_llm() -> ChatOpenAI:
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENAI_ADMIN_KEY")
    if not api_key:
        raise RuntimeError(
            "Missing OpenAI credentials. Set OPENAI_API_KEY or OPENAI_ADMIN_KEY in the environment or .env file."
        )

    return ChatOpenAI(
        model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0,
        api_key=api_key,
    )


llm = _get_llm()


structured_llm = llm.with_structured_output(
    SQLResponse
)


def generate_sql(
    question: str,
    schema: str,
    semantic_context: str,
    previous_sql: str = "",
    error: str = "",
) -> str:

    correction_context = ""

    if previous_sql:

        correction_context = f"""
A previous SQL query failed.

Previous SQL:

{previous_sql}

Error:

{error}

Generate a corrected query.
"""

    prompt = f"""
You are an expert business data analyst
specialized in DuckDB SQL.

DATABASE SCHEMA:

{schema}


BUSINESS SEMANTIC LAYER:

{semantic_context}


USER QUESTION:

{question}


{correction_context}


RULES:

1. Generate only SELECT queries.

2. Never use:
INSERT
UPDATE
DELETE
DROP
ALTER
TRUNCATE

3. Use only the sales table.

4. Use only columns available
in the provided schema.

5. When the user refers to a business
metric, strictly follow the definition
provided in the semantic layer.

6. Do not invent business formulas.

7. Prefer semantic definitions over
your own interpretation.

8. Generate valid DuckDB SQL.
"""

    response = structured_llm.invoke(
        prompt
    )

    return response.sql