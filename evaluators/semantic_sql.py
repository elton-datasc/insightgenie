def evaluate_semantic_sql(
    question: str,
    sql: str,
) -> dict:

    question_lower = question.lower()
    sql_lower = sql.lower()

    problems = []

    if "fevereiro" in question_lower:

        if "'2026-02'" not in sql_lower:

            problems.append(
                "February was not mapped to 2026-02."
            )

    if "janeiro" in question_lower:

        if "'2026-01'" not in sql_lower:

            problems.append(
                "January was not mapped to 2026-01."
            )

    if "margem" in question_lower:

        if "revenue" not in sql_lower or "cost" not in sql_lower:

            problems.append(
                "Margin must use revenue and cost."
            )

    if "positivad" in question_lower:

        if "active = 1" not in sql_lower:

            problems.append(
                "Positivation must filter active = 1."
            )

    if problems:

        return {
            "passed": False,
            "score": 0.0,
            "details": " ".join(problems),
        }

    return {
        "passed": True,
        "score": 1.0,
        "details": "SQL respects known business semantics.",
    }