"""These tests run without a desktop, Tkinter, Pillow, or other dependencies."""
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from debate_timer.formatting import format_time
from debate_timer.models import PhaseSettings
from debate_timer.phases import build_phases
from debate_timer.storage import load_config, save_config


class PhaseTests(unittest.TestCase):
    def test_default_debate_has_20_ordered_turns_and_two_conclusions(self):
        phases = build_phases(PhaseSettings())
        self.assertEqual(len(phases), 20)
        self.assertEqual(phases[0].team, "Ambos equipos")
        self.assertEqual([p.team for p in phases[1:3]], ["Equipo a favor", "Equipo en contra"])
        self.assertEqual([p.kind for p in phases[17:19]], ["conclusion", "conclusion"])
        self.assertEqual(phases[-1].team, "Jurado")
        self.assertEqual([p.ms for p in phases],
                         [60000, 180000, 180000] + [40000, 60000, 40000, 60000] * 3
                         + [300000, 300000, 180000, 180000, 300000])

    def test_question_answer_roles_and_units_follow_custom_settings(self):
        phases = build_phases(PhaseSettings(favor="A", against="B", question_sec=25,
                             answer_min=2, conclusion_min=4, short_warning_sec=5))
        self.assertEqual([(p.name, p.team) for p in phases[3:7]],
                         [("Pregunta 1", "A pregunta"), ("Respuesta 1", "B responde"),
                          ("Pregunta 1", "B pregunta"), ("Respuesta 1", "A responde")])
        self.assertEqual(phases[3].ms, 25000)
        self.assertEqual(phases[4].ms, 120000)
        self.assertEqual(phases[17].ms, 240000)
        self.assertEqual(phases[3].warning_at_ms, 5000)


class FormattingTests(unittest.TestCase):
    def test_tenths_and_minute_boundaries(self):
        self.assertEqual(format_time(60000), "01:00.0")
        self.assertEqual(format_time(59999), "00:59.9")
        self.assertEqual(format_time(123456), "02:03.4")
        self.assertEqual(format_time(0), "00:00.0")

    def test_whole_seconds_and_negative_times(self):
        self.assertEqual(format_time(59999, show_tenths=False), "00:59")
        self.assertEqual(format_time(-10), "00:00.0")


class StorageTests(unittest.TestCase):
    def test_unicode_and_projector_sizes_round_trip(self):
        data = {"titulo": "Conclusión · Historia", "tamanos_interfaz": {"clock": {"font_size": 90}}}
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "debate.json"
            save_config(path, data)
            self.assertEqual(load_config(path), data)
            self.assertIn("Conclusión", path.read_text(encoding="utf-8"))

    def test_invalid_configuration_reports_parse_error(self):
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "debate.json"
            path.write_text("not json", encoding="utf-8")
            with self.assertRaises(json.JSONDecodeError):
                load_config(path)

    def test_domain_imports_do_not_load_tkinter(self):
        subprocess.run([sys.executable, "-B", "-c",
                        "import sys; import debate_timer.phases, debate_timer.storage, debate_timer.formatting; "
                        "assert 'tkinter' not in sys.modules"], check=True)


if __name__ == "__main__":
    unittest.main()
