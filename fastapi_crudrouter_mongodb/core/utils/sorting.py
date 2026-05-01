def normalize_order_by(order_by: str | None) -> int:
    if order_by is None:
        return 1

    normalized_value = order_by.upper()
    if normalized_value == "ASC":
        return 1
    if normalized_value == "DESC":
        return -1

    raise ValueError("order_by must be either 'ASC' or 'DESC'")
