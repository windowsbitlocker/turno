"""JSON configuration persistence, independent of dialogs and Tkinter."""
import json
from pathlib import Path


def load_config(path: str | Path):
    with open(path, "r", encoding="utf-8") as source:
        return json.load(source)


def save_config(path: str | Path, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as destination:
        json.dump(data, destination, ensure_ascii=False, indent=2)
