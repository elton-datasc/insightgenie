from graph.workflow import graph
from database.duckdb_client import DatabaseClient
from observability.langwatch_client import setup_langwatch
import langwatch
from uuid import uuid4

setup_langwatch()

@langwatch.trace(name="InsightGenie Query")
def run_query(question: str, schema: str):
    trace = langwatch.get_current_trace()
    interaction_id = str(uuid4())
    trace.update(
    metadata={
        "interaction_id": interaction_id,
        "agent": "InsightGenie",
        "agent_version": "v5",
        "database": "duckdb",
        "workflow": "langgraph",
    }
)

    initial_state = {
        "interaction_id": interaction_id,
        "question": question,
        "normalized_question": "",
        "schema": schema,
        "semantic_context": "",
        "sql": "",
        "query_result": "",
        "answer": "",
        "error": "",
        "retry_count": 0,
    }

    result = graph.invoke(initial_state)

    return result

database = DatabaseClient()
database.load_data("data/sales.csv")

schema = database.get_schema().to_string()


while True:

    question = input("\nPergunta: ")

    if question.lower() == "sair":
        break

    result = run_query(
        question=question,
        schema=schema,
    )

    print("\nSQL final:")
    print(result["sql"])

    print(
        "\nTentativas de correção:",
        result["retry_count"],
    )

    if result["query_result"]:
        print("\nResultado SQL:")
        print(result["query_result"])

    print("\nInsightGenie:")
    print(result["answer"])