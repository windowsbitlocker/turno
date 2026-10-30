"""Validated, data-only block templates. No UI or executable scripting is involved."""
from copy import deepcopy
from dataclasses import dataclass, field
import uuid

from .models import Phase, PhaseSettings, RebuttalRule
from .phases import build_phases

MAX_PHASES = 500
MAX_DEPTH = 8
KINDS = {
    "preparation": "Preparación", "speech": "Discurso", "questions": "Preguntas",
    "answer": "Respuesta", "conclusion": "Conclusión", "break": "Pausa", "jury": "Jurado",
}


def new_id():
    return uuid.uuid4().hex[:12]


@dataclass
class Team:
    id: str
    name: str


@dataclass
class Robo:
    team_id: str
    seconds: int = 60
    window_seconds: int = 120
    deduct: bool = True


@dataclass
class StageBlock:
    name: str = "Discurso"
    kind: str = "speech"
    team_id: str | None = None
    seconds: int = 180
    warning_seconds: int = 30
    role: str = ""
    shared_label: str = "Ambos equipos"
    robo: Robo | None = None
    id: str = field(default_factory=new_id)


@dataclass
class RepeatBlock:
    count: int = 2
    blocks: list = field(default_factory=list)
    id: str = field(default_factory=new_id)


@dataclass
class DebateTemplate:
    name: str = "Mi formato"
    teams: list[Team] = field(default_factory=lambda: [Team("a", "Equipo A"), Team("b", "Equipo B")])
    blocks: list = field(default_factory=list)

    def clone(self):
        return deepcopy(self)


def _text(value, label, empty=False):
    if not isinstance(value, str) or len(value) > 200 or (not empty and not value.strip()):
        raise ValueError(f"{label}: escribe un texto válido (máximo 200 caracteres).")


def _integer(value, low, high, label):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"{label}: debe ser un entero entre {low} y {high}.")


def compile_template(template: DebateTemplate) -> list[Phase]:
    _text(template.name, "Nombre del formato")
    if not isinstance(template.teams, list) or len(template.teams) > 32:
        raise ValueError("El formato admite hasta 32 equipos.")
    teams = {}
    for team in template.teams:
        _text(team.id, "Identificador de equipo")
        _text(team.name, "Nombre de equipo")
        if team.id in teams:
            raise ValueError("Hay identificadores de equipo repetidos.")
        teams[team.id] = team.name.strip()
    phases, identifiers = [], set()

    def validate(blocks, depth=0):
        if depth > MAX_DEPTH or not isinstance(blocks, list) or len(blocks) > MAX_PHASES:
            raise ValueError("La plantilla tiene demasiados bloques o niveles de repetición.")
        for block in blocks:
            if not isinstance(block, (StageBlock, RepeatBlock)):
                raise ValueError("Tipo de bloque desconocido.")
            _text(block.id, "Identificador de bloque")
            if block.id in identifiers:
                raise ValueError("Hay identificadores de bloque repetidos.")
            identifiers.add(block.id)
            if len(identifiers) > MAX_PHASES:
                raise ValueError("La plantilla tiene demasiados bloques.")
            if isinstance(block, RepeatBlock):
                _integer(block.count, 1, 20, "Repeticiones")
                if not block.blocks:
                    raise ValueError("Una repetición necesita al menos un bloque dentro.")
                validate(block.blocks, depth+1)
                continue
            _text(block.name, "Nombre de etapa")
            if block.kind not in KINDS:
                raise ValueError("Tipo de etapa desconocido.")
            _integer(block.seconds, 1, 86400, "Duración en segundos")
            _integer(block.warning_seconds, 0, block.seconds, "Aviso en segundos")
            _text(block.role, "Rol", empty=True)
            _text(block.shared_label, "Participante común", empty=True)
            if block.team_id is not None and block.team_id not in teams:
                raise ValueError(f"{block.name}: selecciona un equipo existente.")
            if block.robo:
                rule = block.robo
                if not isinstance(rule, Robo) or rule.team_id not in teams or rule.team_id == block.team_id:
                    raise ValueError(f"{block.name}: el equipo del robo debe ser distinto y existir.")
                _integer(rule.seconds, 1, 86400, "Duración del robo")
                _integer(rule.window_seconds, 1, block.seconds, "Ventana de solicitud del robo")
                if type(rule.deduct) is not bool:
                    raise ValueError("La opción de descuento debe ser verdadera o falsa.")
    validate(template.blocks)

    def expand(blocks):
        for block in blocks:
            if isinstance(block, RepeatBlock):
                for _ in range(block.count):
                    expand(block.blocks)
                continue
            speaker = teams[block.team_id] if block.team_id is not None else block.shared_label.strip() or "Todos"
            if block.role.strip():
                speaker += " " + block.role.strip()
            rule = None
            if block.robo:
                rule = RebuttalRule(teams[block.robo.team_id], block.robo.seconds*1000,
                                     block.robo.window_seconds*1000, block.robo.deduct)
            phases.append(Phase(block.name.strip(), speaker, block.seconds*1000,
                                block.warning_seconds*1000, block.kind, True, rule))
            if len(phases) > MAX_PHASES:
                raise ValueError(f"El formato no puede superar {MAX_PHASES} turnos al expandir repeticiones.")
    expand(template.blocks)
    if not phases:
        raise ValueError("Añade al menos una etapa al formato.")
    return phases


def template_to_dict(template):
    compile_template(template)
    def block_data(block):
        if isinstance(block, RepeatBlock):
            return {"type": "repeat", "id": block.id, "count": block.count,
                    "blocks": [block_data(child) for child in block.blocks]}
        data = {"type": "stage", "id": block.id, "name": block.name, "kind": block.kind,
                "team_id": block.team_id, "seconds": block.seconds,
                "warning_seconds": block.warning_seconds, "role": block.role,
                "shared_label": block.shared_label, "robo": None}
        if block.robo:
            data["robo"] = vars(block.robo).copy()
        return data
    return {"format": "turno-template", "version": 1, "name": template.name,
            "teams": [vars(team).copy() for team in template.teams],
            "blocks": [block_data(block) for block in template.blocks]}


def template_from_dict(data):
    if not isinstance(data, dict) or data.get("format") != "turno-template" or type(data.get("version")) is not int or data["version"] != 1:
        raise ValueError("El archivo no es una plantilla Turno de versión 1.")
    try:
        teams = [Team(**team) for team in data["teams"]]
        parsed_count = 0
        def parse(blocks, depth=0):
            nonlocal parsed_count
            if depth > MAX_DEPTH or not isinstance(blocks, list) or len(blocks) > MAX_PHASES:
                raise ValueError("Demasiados bloques o niveles de repetición.")
            result = []
            for value in blocks:
                parsed_count += 1
                if parsed_count > MAX_PHASES:
                    raise ValueError("La plantilla tiene demasiados bloques.")
                value = value.copy()
                kind = value.pop("type")
                if kind == "repeat":
                    value["blocks"] = parse(value["blocks"], depth+1)
                    block = RepeatBlock(**value)
                elif kind == "stage":
                    if value.get("robo") is not None:
                        value["robo"] = Robo(**value["robo"])
                    block = StageBlock(**value)
                else:
                    raise ValueError("Tipo de bloque desconocido.")
                result.append(block)
            return result
        template = DebateTemplate(data["name"], teams, parse(data["blocks"]))
        compile_template(template)
        return template
    except (KeyError, TypeError, AttributeError) as error:
        raise ValueError("La estructura del archivo de plantilla no es válida.") from error


def school_template(settings=None, steal_seconds=60, window_seconds=120):
    settings = settings or PhaseSettings()
    phases = build_phases(settings)
    teams = [Team("a", settings.favor), Team("b", settings.against)]
    owners = [None, "a", "b"] + ["a", "b", "b", "a"]*3 + ["a", "b", "a", "b", None]
    blocks = []
    for phase, owner in zip(phases, owners):
        role = "pregunta" if phase.name.startswith("Pregunta") else "responde" if phase.name.startswith("Respuesta") else ""
        kind = "conclusion" if phase.kind == "conclusion" else "preparation" if phase.name.startswith("Preparación") else "questions" if role == "pregunta" else "answer" if role else "jury" if owner is None and phase.team == "Jurado" else "speech"
        robo = Robo("b" if owner == "a" else "a", steal_seconds, window_seconds) if phase.kind == "conclusion" else None
        blocks.append(StageBlock(phase.name, kind, owner, phase.ms//1000, phase.warning_at_ms//1000,
                                 role, phase.team if owner is None else "", robo))
    return DebateTemplate("Debate escolar", teams, blocks)


def quick_template():
    return DebateTemplate("Temporizador simple", [], [StageBlock("Tiempo libre", seconds=300)])


def find_block(template, identity):
    def find(blocks, ancestors):
        for index, block in enumerate(blocks):
            if block.id == identity:
                return blocks, index, ancestors
            if isinstance(block, RepeatBlock):
                found = find(block.blocks, ancestors+[block.id])
                if found:
                    return found
        return None
    return find(template.blocks, [])


def move_block(template, identity, target_parent=None, target_index=None):
    found = find_block(template, identity)
    if not found:
        raise ValueError("Bloque no encontrado.")
    source, index, _ = found
    block = source[index]
    destination = template.blocks
    if target_parent:
        parent_found = find_block(template, target_parent)
        if not parent_found or not isinstance(parent_found[0][parent_found[1]], RepeatBlock):
            raise ValueError("El destino debe ser una repetición.")
        if target_parent == identity or identity in parent_found[2]:
            raise ValueError("No se puede mover una repetición dentro de sí misma.")
        destination = parent_found[0][parent_found[1]].blocks
    position = len(destination) if target_index is None else max(0, min(target_index, len(destination)))
    if source is destination and index < position:
        position -= 1
    source.pop(index)
    destination.insert(position, block)


def duplicate_block(block):
    result = deepcopy(block)
    def reidentify(value):
        value.id = new_id()
        if isinstance(value, RepeatBlock):
            for child in value.blocks:
                reidentify(child)
    reidentify(result)
    return result
