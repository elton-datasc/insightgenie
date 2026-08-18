from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


class SQLResponse(BaseModel):
    sql: str = Field(
        description="SQL query generated from the user question"
    )


llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


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