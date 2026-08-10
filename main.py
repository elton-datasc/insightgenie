from database.duckdb_client import DatabaseClient
from agents.sql_agent import generate_sql


database = DatabaseClient()

database.load_data("data/sales.csv")

schema = database.get_schema().to_string()


while True:

    question = input("\nPergunta: ")

    if question.lower() == "sair":
        break

    sql = generate_sql(
        question=question,
        schema=schema
    )

    print("\nSQL gerado:")

    print(sql)

    result = database.execute(sql)

    print("\nResultado:")

    print(result)