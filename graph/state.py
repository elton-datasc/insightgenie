from typing import TypedDict


class AgentState(TypedDict):
    question: str
    schema: str
    sql: str
    query_result: str
    answer: str
    error: str
    retry_count: int