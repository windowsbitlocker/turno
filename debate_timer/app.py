"""Application assembly, shared state, and window lifecycle."""
import tkinter as tk
from typing import List
from .models import Phase
from .ui.size_editor import SizeEditor
from .ui.styles import StyleMixin
from .ui.settings import SettingsPanelMixin
from .ui.operator import OperatorPanelMixin
from .ui.projector import ProjectorMixin
from .ui.logos import LogoMixin
from .ui.presenter import PresenterMixin
from .shortcuts import ShortcutMixin
from .timing import TimingMixin
from .rebuttal import RebuttalMixin
from .configuration import ConfigurationMixin


class TemporizadorDebate(StyleMixin, SettingsPanelMixin, OperatorPanelMixin, ProjectorMixin, LogoMixin, PresenterMixin, ShortcutMixin, TimingMixin, RebuttalMixin, ConfigurationMixin):
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Controles del Temporizador")

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        # Ventana de control: tamaño inicial cómodo, pero siempre libre de achicarse o
        # agrandarse — el mínimo nunca depende del tamaño inicial, así el resize real
        # (arrastrando el borde) no queda bloqueado en ningún escenario.
        control_w = max(480, min(660, screen_w - 80))
        control_h = max(560, min(800, screen_h - 100))
        control_x = 20
        control_y = 20
        self.root.geometry(f"{control_w}x{control_h}+{control_x}+{control_y}")
        self.root.minsize(480, 620)
        self.root.maxsize(screen_w, screen_h)
        self.root.resizable(True, True)

        self.display = tk.Toplevel(self.root)
        self.display.title("Pantalla del Temporizador")

        # Ventana de proyección: ocupa la mayor parte de la pantalla disponible, centrada.
        display_w = int(screen_w * 0.85)
        display_h = int(screen_h * 0.85)
        display_x = (screen_w - display_w) // 2
        display_y = (screen_h - display_h) // 2
        self.display.geometry(f"{display_w}x{display_h}+{display_x}+{display_y}")
        self.display.minsize(500, 350)
        self.display.resizable(True, True)
        self.display.configure(bg="#000000")

        self.logo_paths: List[str] = []
        self.logo_imgs = []

        self.setup_styles()

        self.phases: List[Phase] = []
        self.phase_index = 0

        self.remaining_ms = 0
        self.running = False
        self.after_id = None
        self.last_tick_time = None

        self.last_steal_note = ""
        self.steal_used_this_phase = False

        self.robo_active = False
        self.robo_team = ""
        self.robo_remaining_ms = 0
        self.robo_max_ms = 0


        self.build_variables()
        self.bind_shortcuts()
        self.build_control_window()
        self.build_display_window()
        self.rebuild_phases()
        self.load_phase(0)
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)
        self.display.protocol("WM_DELETE_WINDOW", self.display.withdraw)
        self.size_editor = SizeEditor(self)

    def configure_auto_size(self, widget, **options):
        editor = getattr(self, "size_editor", None)
        allowed = {name: value for name, value in options.items()
                   if not editor or not editor.customized(widget, "font_size" if name == "font" else name)}
        if allowed:
            widget.configure(**allowed)

    def run(self):
        self.root.mainloop()

    def close_app(self):
        # Cancel callbacks before destroying their Tk commands (also editor updates).
        for callback in self.root.tk.call("after", "info"):
            self.root.after_cancel(callback)
        self.root.destroy()
