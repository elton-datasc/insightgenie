FORBIDDEN_COMMANDS = {
    "delete",
    "drop",
    "update",
    "insert",
    "alter",
    "truncate",
}


def evaluate_sql_validity(sql: str) -> dict:

    normalized = sql.strip().lower()

    if not normalized.startswith("select"):
        return {
            "passed": False,
            "score": 0.0,
            "details": "Query is not a SELECT statement.",
        }

    for command in FORBIDDEN_COMMANDS:

        if command in normalized:

            return {
                "passed": False,
                "score": 0.0,
                "details": (
                    f"Forbidden command detected: {command}"
                ),
            }

    return {
        "passed": True,
        "score": 1.0,
        "details": "SQL passed safety validation.",
    }