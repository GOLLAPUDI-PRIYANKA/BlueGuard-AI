import uuid


def generate_id(prefix: str) -> str:
    short = uuid.uuid4().hex[:8].upper()
    return f"{prefix}{short}"
