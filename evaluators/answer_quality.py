from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


class AnswerEvaluation(BaseModel):
    score: float = Field(
        ge=0,
        le=1,
    )

    passed: bool

    explanation: str


judge = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
).with_structured_output(
    AnswerEvaluation
)


def evaluate_groundedness(
    question: str,
    query_result: str,
    answer: str,
) -> AnswerEvaluation:

    prompt = f"""
You are evaluating an analytics assistant.

Determine whether the final answer is fully
supported by the SQL query result.

QUESTION:

{question}

DATABASE RESULT:

{query_result}

ANSWER:

{answer}

Evaluation rules:

- Do not judge whether the SQL itself was correct.
- Evaluate only whether the answer is supported
  by the provided database result.
- Score from 0 to 1.
- Pass when score >= 0.8.
"""

    return judge.invoke(prompt)


def evaluate_hallucination(
    query_result: str,
    answer: str,
) -> AnswerEvaluation:

    prompt = f"""
Evaluate whether the answer contains factual
claims that are not present in or supported
by the database result.

DATABASE RESULT:

{query_result}

ANSWER:

{answer}

Score:

1.0 = no hallucination
0.0 = strongly hallucinated

Pass when score >= 0.8.
"""

    return judge.invoke(prompt)

