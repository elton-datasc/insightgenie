import duckdb


class DatabaseClient:

    def __init__(self):
        self.connection = duckdb.connect(":memory:")

    def load_data(self, path: str):
        self.connection.execute(
            f"""
            CREATE TABLE sales AS
            SELECT *
            FROM read_csv_auto('{path}')
            """
        )

    def execute(self, sql: str):
        return self.connection.execute(sql).df()

    def get_schema(self):
        return self.connection.execute(
            "DESCRIBE sales"
        ).df()