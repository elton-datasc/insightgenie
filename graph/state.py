from typing import TypedDict

class AgentState(TypedDict):
    interaction_id: str

    question: str
    normalized_question: str

    schema: str
    semantic_context: str

    sql: str
    query_result: str

    answer: str
    error: str

    retry_count: int

