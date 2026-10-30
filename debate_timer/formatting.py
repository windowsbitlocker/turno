"""Clock formatting shared by operator and audience displays."""


def format_time(ms: int, show_tenths: bool = True) -> str:
    ms = max(0, int(ms))
    total_seconds = ms // 1000
    minutes, seconds = divmod(total_seconds, 60)
    text = f"{minutes:02d}:{seconds:02d}"
    return f"{text}.{(ms % 1000) // 100}" if show_tenths else text
