"""Data structures shared by phase construction and the application."""
from dataclasses import dataclass


@dataclass
class Phase:
    name: str
    team: str
    ms: int
    warning_at_ms: int = 0
    kind: str = "normal"


@dataclass(frozen=True)
class PhaseSettings:
    favor: str = "Equipo a favor"
    against: str = "Equipo en contra"
    prep_min: int = 1
    opening_min: int = 3
    question_sec: int = 40
    answer_min: int = 1
    final_prep_min: int = 5
    conclusion_min: int = 3
    jury_min: int = 5
    opening_warning_sec: int = 30
    short_warning_sec: int = 10
    jury_warning_sec: int = 60
