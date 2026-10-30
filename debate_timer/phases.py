"""Build the debate's ordered 20 phases without depending on Tkinter."""
from .models import Phase, PhaseSettings


def build_phases(settings: PhaseSettings) -> list[Phase]:
    favor, against = settings.favor, settings.against
    short_warning = settings.short_warning_sec * 1_000
    opening_warning = settings.opening_warning_sec * 1_000
    question = settings.question_sec * 1_000
    answer = settings.answer_min * 60_000
    phases = [
        Phase("Preparación", "Ambos equipos", settings.prep_min * 60_000, short_warning),
        Phase("Presentación inicial", favor, settings.opening_min * 60_000, opening_warning),
        Phase("Presentación inicial", against, settings.opening_min * 60_000, opening_warning),
    ]
    for number in range(1, 4):
        phases.extend([
            Phase(f"Pregunta {number}", favor + " pregunta", question, short_warning),
            Phase(f"Respuesta {number}", against + " responde", answer, short_warning),
            Phase(f"Pregunta {number}", against + " pregunta", question, short_warning),
            Phase(f"Respuesta {number}", favor + " responde", answer, short_warning),
        ])
    phases.extend([
        Phase("Preparación final", favor, settings.final_prep_min * 60_000, short_warning),
        Phase("Preparación final", against, settings.final_prep_min * 60_000, short_warning),
        Phase("Conclusión", favor, settings.conclusion_min * 60_000, opening_warning, kind="conclusion"),
        Phase("Conclusión", against, settings.conclusion_min * 60_000, opening_warning, kind="conclusion"),
        Phase("Deliberación del jurado", "Jurado", settings.jury_min * 60_000, settings.jury_warning_sec * 1_000),
    ])
    return phases
