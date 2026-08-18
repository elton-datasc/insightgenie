import sys

import pytest


def test_missing_credentials_raise_clear_error(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_ADMIN_KEY", raising=False)
    sys.modules.pop("agents.sql_agent", None)

    import agents.sql_agent as sql_agent

    with pytest.raises(RuntimeError, match="OPENAI_API_KEY|OPENAI_ADMIN_KEY"):
        sql_agent._get_llm()
