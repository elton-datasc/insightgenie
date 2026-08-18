from graph.workflow import graph
from database.duckdb_client import DatabaseClient


database = DatabaseClient()
database.load_data("data/sales.csv")

schema = database.get_schema().to_string()


while True:

    question = input(
        "\nPergunta: "
    )

    if question.lower() == "sair":
        break

    initial_state = {
    "question": question,
    "schema": schema,
    "semantic_context": "",
    "sql": "",
    "query_result": "",
    "answer": "",
    "error": "",
    "retry_count": 0,
}

    result = graph.invoke(
        initial_state
    )

    print("\nSQL final:")
    print(
        result["sql"]
    )

    print(
        "\nTentativas de correção:",
        result["retry_count"]
    )

    if result["query_result"]:

        print("\nResultado SQL:")
        print(
            result["query_result"]
        )

    print("\nInsightGenie:")
    print(
        result["answer"]
    )