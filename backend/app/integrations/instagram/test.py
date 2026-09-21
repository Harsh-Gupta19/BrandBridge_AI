def add(a: float, b: float) -> float:
    """Return the sum of two numbers."""
    return a + b


def divide(a: float, b: float) -> float:
    """Divide a by b. Raises ValueError if b is zero."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
