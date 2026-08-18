BUSINESS_METRICS = {
    "revenue": {
        "name": "Receita",
        "description": "Valor total de receita obtida com vendas.",
        "formula": "SUM(revenue)",
        "columns": ["revenue"],
    },

    "volume": {
        "name": "Volume",
        "description": "Quantidade total vendida no período.",
        "formula": "SUM(volume)",
        "columns": ["volume"],
    },

    "margin": {
        "name": "Margem",
        "description": (
            "Valor financeiro obtido pela diferença "
            "entre receita e custo."
        ),
        "formula": "SUM(revenue - cost)",
        "columns": ["revenue", "cost"],
    },

    "margin_percentage": {
        "name": "Margem percentual",
        "description": (
            "Percentual da receita que permanece "
            "após descontar os custos."
        ),
        "formula": (
            "(SUM(revenue) - SUM(cost)) "
            "/ NULLIF(SUM(revenue), 0) * 100"
        ),
        "columns": ["revenue", "cost"],
    },

    "active_customer": {
        "name": "Cliente positivado",
        "description": (
            "Cliente que realizou compra no período analisado."
        ),
        "formula": "active = 1",
        "columns": ["active"],
    },

    "positivation": {
        "name": "Positivação",
        "description": (
            "Quantidade de clientes distintos que realizaram "
            "compra no período."
        ),
        "formula": (
            "COUNT(DISTINCT CASE "
            "WHEN active = 1 THEN customer_id END)"
        ),
        "columns": [
            "active",
            "customer_id",
        ],
    },
}


BUSINESS_DIMENSIONS = {
    "customer": {
        "name": "Cliente",
        "description": "Cliente responsável pela operação.",
        "column": "customer_name",
    },

    "region": {
        "name": "Região",
        "description": "Região geográfica do cliente.",
        "column": "region",
    },

    "month": {
        "name": "Mês",
        "description": "Mês de referência da operação.",
        "column": "month",
    },
}