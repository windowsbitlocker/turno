"""Integration checks for the local operator timer and projector."""
import unittest
from unittest.mock import patch
from debate_timer.app import TemporizadorDebate

class TimerIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.app = TemporizadorDebate()
        self.app.root.withdraw()
        self.app.display.withdraw()

    def tearDown(self):
        self.app.close_app()

    def test_operator_robo_deducts_only_time_used(self):
        self.app.load_phase(17)
        self.app.start()
        self.app.steal_button.invoke()
        self.assertTrue(self.app.robo_active)
        self.assertEqual(self.app.robo_team, self.app.team_against_var.get())
        before = self.app.remaining_ms
        timestamp = self.app.last_tick_time
        with patch('debate_timer.timing.time.perf_counter', return_value=timestamp + 5):
            self.app.end_steal_button.invoke()
        self.assertEqual(self.app.remaining_ms, before - 5000)
        self.assertFalse(self.app.running)
        self.assertFalse(self.app.robo_active)
        self.assertTrue(self.app.steal_used_this_phase)

    def test_phase_navigation_and_reset(self):
        self.assertEqual(len(self.app.phases), 20)
        self.app.next_phase()
        self.assertEqual(self.app.phase_index, 1)
        self.app.adjust_time(-10000)
        self.app.reset_current()
        self.assertEqual(self.app.remaining_ms, self.app.current_phase().ms)
        self.app.previous_phase()
        self.assertEqual(self.app.phase_index, 0)
        self.assertFalse(self.app.running)

    def test_operator_start_pause_and_configuration(self):
        self.app.start_pause_button.invoke()
        self.assertTrue(self.app.running)
        self.app.start_pause_button.invoke()
        self.assertFalse(self.app.running)
        config = self.app.get_config()
        config['titulo'] = 'Debate escolar'
        self.app.apply_config(config)
        self.assertEqual(self.app.display_title_label['text'], 'Debate escolar')

    def test_tick_preserves_fraction_and_pause_accounts_elapsed(self):
        self.app.running = True
        self.app.last_tick_time = 100.0
        self.app.remaining_ms = 1000
        with patch('debate_timer.timing.time.perf_counter', return_value=100.0307):
            self.app.tick()
        self.assertEqual(self.app.remaining_ms, 970)
        self.assertAlmostEqual(self.app.last_tick_time, 100.030)
        with patch('debate_timer.timing.time.perf_counter', return_value=100.045):
            self.app.pause()
        self.assertLessEqual(abs(self.app.remaining_ms - 955), 1)

    def test_manual_sizes_remain_during_resize_and_timer_updates(self):
        from tkinter import font as tkfont
        from types import SimpleNamespace
        editor = self.app.size_editor
        self.app.start()
        editor.set_value(self.app.display_timer_label, 'font_size', 90)
        editor.set_value(self.app.display_title_label, 'font_size', 28)
        self.app.resize_controls(SimpleNamespace(width=500, height=540))
        self.app.resize_display()
        self.app.update_all_labels()
        self.assertTrue(self.app.running)
        self.assertEqual(tkfont.Font(font=self.app.display_timer_label['font']).actual('size'), 90)
        self.assertEqual(tkfont.Font(font=self.app.display_title_label['font']).actual('size'), 28)
        self.assertEqual(self.app.start_pause_button['width'], 18)

    def test_size_editor_opens_for_every_element_and_restores_settings(self):
        from tkinter import font as tkfont
        editor = self.app.size_editor
        for widget in list(editor.widgets.values()):
            editor.open(widget)
        editor.set_value(self.app.display_timer_label, 'font_size', 57)
        config = self.app.get_config()
        editor.reset(self.app.display_timer_label)
        self.app.apply_config(config)
        self.assertEqual(tkfont.Font(font=self.app.display_timer_label['font']).actual('size'), 57)

    def test_slider_mouse_drag_and_number_field_change_the_target(self):
        import tkinter as tk
        from tkinter import font as tkfont
        editor = self.app.size_editor
        editor.open(self.app.display_timer_label)
        self.app.root.update()
        slider = next(widget for widget in editor.controls.winfo_children() if isinstance(widget, tk.Scale))
        before = slider.get()
        x, y = slider.coords(before)
        slider.event_generate('<ButtonPress-1>', x=x, y=y)
        slider.event_generate('<B1-Motion>', x=x+25, y=y)
        slider.event_generate('<ButtonRelease-1>', x=x+25, y=y)
        self.app.root.update()
        self.assertGreater(slider.get(), before)
        self.assertEqual(tkfont.Font(font=self.app.display_timer_label['font']).actual('size'), slider.get())
        slider.variable_reference.set('42')
        self.app.root.update()
        self.assertEqual(slider.get(), 42)
        self.assertEqual(tkfont.Font(font=self.app.display_timer_label['font']).actual('size'), 42)

    def test_operator_elements_and_old_operator_sizes_are_excluded(self):
        editor = self.app.size_editor
        self.assertTrue(all(widget.winfo_toplevel() is self.app.display for widget in editor.widgets.values()))
        self.assertFalse(editor.editable(self.app.current_time_label))
        self.assertFalse(self.app.root.bind('<Button-3>'))
        with self.assertRaises(ValueError):
            editor.set_value(self.app.start_pause_button, 'width', 100)
        editor.restore({str(self.app.start_pause_button): {'width': 100},
                        str(self.app.display_timer_label): {'font_size': 80}})
        self.assertEqual(self.app.start_pause_button['width'], 18)
        self.assertNotIn(str(self.app.start_pause_button), editor.export())
        editor.open()
        self.assertIs(editor.target, self.app.display_timer_label)

if __name__ == '__main__':
    unittest.main()
