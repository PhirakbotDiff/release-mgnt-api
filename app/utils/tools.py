def calc_percentage(current: int, previous: int):
    if previous == 0:
        if current > 0:
            return 100.0, "up"
        return 0.0, "up"

    change = ((current - previous) / previous) * 100
    trend = "up" if change >= 0 else "down"
    return round(abs(change), 2), trend