from types import SimpleNamespace
from unittest.mock import patch
import unittest
from debate_timer.app import TemporizadorDebate
from debate_timer.templates import (DebateTemplate, Team, StageBlock, RepeatBlock, Robo,
                                    compile_template, template_to_dict)
from debate_timer.ui.block_editor import BlockEditor


class BlockEditorTests(unittest.TestCase):
    def setUp(self):
        self.app = TemporizadorDebate()
        self.app.root.withdraw()
        self.app.display.withdraw()

    def tearDown(self):
        self.app.close_app()

    def test_editor_drafts_do_not_interrupt_running_clock_and_repeat_applies(self):
        self.app.start()
        editor = BlockEditor(self.app, DebateTemplate())
        editor.add_repeat()
        group = editor.block()
        editor.add_stage("questions")
        editor.add_stage("answer")
        editor.select(group.id)
        editor.fields["count"].set("3")
        editor.save_block()
        self.assertTrue(self.app.running)
        self.assertIsNone(self.app.active_template)
        self.assertEqual(len(self.app.phases), 20)
        with patch("debate_timer.ui.block_editor.messagebox.askyesno", return_value=True):
            editor.apply()
        self.assertFalse(self.app.running)
        self.assertEqual(len(self.app.phases), 6)
        self.assertEqual(self.app.phase_index, 0)
        group.blocks.clear()
        self.assertEqual(len(compile_template(self.app.active_template)), 6)

    def test_canvas_drag_reorders_blocks(self):
        template = DebateTemplate(blocks=[StageBlock("First"), StageBlock("Second"), StageBlock("Third")])
        editor = BlockEditor(self.app, template)
        self.app.root.update()
        rows = list(editor.rows)
        canvas = editor.canvas
        canvas.event_generate("<ButtonPress-1>", x=30, y=int(rows[0]["top"]+20))
        canvas.event_generate("<B1-Motion>", x=30, y=int(rows[2]["top"]+10))
        canvas.event_generate("<ButtonRelease-1>", x=30, y=int(rows[2]["top"]+10))
        self.app.root.update()
        self.assertEqual([block.name for block in editor.draft.blocks], ["Second", "First", "Third"])
        editor.undo()
        self.assertEqual([block.name for block in editor.draft.blocks], ["First", "Second", "Third"])
        editor.redo()
        self.assertEqual([block.name for block in editor.draft.blocks], ["Second", "First", "Third"])

    def test_invalid_template_leaves_clock_and_configuration_untouched(self):
        self.app.start()
        bad = DebateTemplate(blocks=[StageBlock(seconds=0)])
        with self.assertRaises(ValueError):
            self.app.apply_template(bad)
        self.assertTrue(self.app.running)
        self.assertEqual(len(self.app.phases), 20)
        original_title = self.app.title_var.get()
        with self.assertRaises(ValueError):
            self.app.apply_config({"titulo": "Must not apply", "plantilla": {"format": "bad"}})
        self.assertEqual(self.app.title_var.get(), original_title)
        self.assertTrue(self.app.running)

    def test_custom_conclusion_has_no_implicit_robo(self):
        self.app.apply_template(DebateTemplate(blocks=[StageBlock("Closing", "conclusion", "a")]))
        self.assertIsNone(self.app.current_steal_rule())
        self.assertFalse(self.app.steal_panel.winfo_manager())
        with patch("debate_timer.rebuttal.messagebox.showwarning") as warning:
            self.app.start_steal()
        warning.assert_called_once()
        self.assertFalse(self.app.robo_active)

    def test_robo_can_use_third_team_and_leave_stage_time_untouched(self):
        template = DebateTemplate(teams=[Team("a", "A"), Team("b", "B"), Team("c", "C")],
            blocks=[StageBlock("Speech", team_id="a", robo=Robo("c", 30, 60, False))])
        self.app.apply_template(template)
        self.app.start_steal()
        self.assertEqual(self.app.robo_team, "C")
        before = self.app.remaining_ms
        timestamp = self.app.last_tick_time
        with patch("debate_timer.timing.time.perf_counter", return_value=timestamp+5):
            self.app.end_steal_now()
        self.assertEqual(self.app.remaining_ms, before)
        self.assertFalse(self.app.running)

    def test_template_configuration_round_trip_and_legacy_import(self):
        template = DebateTemplate("Custom", blocks=[StageBlock("Opening", team_id="a"), StageBlock("Closing", team_id="b")])
        self.app.apply_template(template)
        config = self.app.get_config()
        self.app.use_school_format()
        self.assertEqual(len(self.app.phases), 20)
        self.app.apply_config(config)
        self.assertEqual(len(self.app.phases), 2)
        self.assertEqual(template_to_dict(self.app.active_template), template_to_dict(template))
        config.pop("plantilla")
        self.app.apply_config(config)
        self.assertIsNone(self.app.active_template)
        self.assertEqual(len(self.app.phases), 20)

    def test_properties_and_duplicate_remove_preserve_original_block(self):
        editor = BlockEditor(self.app, DebateTemplate(blocks=[StageBlock("Opening")]))
        editor.select(editor.draft.blocks[0].id)
        editor.fields["seconds"].set("02:15")
        editor.fields["warning_seconds"].set("15")
        editor.save_block()
        self.assertEqual(editor.block().seconds, 135)
        editor.duplicate()
        self.assertEqual(len(editor.draft.blocks), 2)
        self.assertNotEqual(editor.draft.blocks[0].id, editor.draft.blocks[1].id)
        editor.remove()
        self.assertEqual(editor.draft.blocks[0].seconds, 135)


if __name__ == "__main__":
    unittest.main()
