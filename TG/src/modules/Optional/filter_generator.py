from typing import List, Tuple, Union
from TG.src.modules.Optional.enums import ProductColumn, FilterOperator


def build_where_clause(
        conditions: List[Tuple[ProductColumn, FilterOperator, Union[str, float, List]]]
) -> Tuple[str, List]:
    """
    Unified version supporting all features
    Returns: (WHERE clause, parameters)
    """
    where_parts = []
    params = []

    for column, operator, value in conditions:
        if operator == FilterOperator.IN:
            if not isinstance(value, list):
                raise ValueError("IN operator requires a list of values")
            placeholders = ','.join(['?'] * len(value))
            where_parts.append(f"{column.value} IN ({placeholders})")
            params.extend(value)
        else:
            where_parts.append(f"{column.value} {operator.value} ?")
            params.append(value)

    return ("WHERE " + " AND ".join(where_parts) if where_parts else "", params)