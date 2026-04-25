def clamp_percentage(value: float) -> float:
    return max(0.0, min(100.0, value))


def round_percentage(value: float) -> float:
    return round(clamp_percentage(value), 2)

