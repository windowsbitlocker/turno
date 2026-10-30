"""Apply validated block templates to the operator's timer."""
from tkinter import messagebox
from .templates import compile_template, school_template


class TemplateMixin:
    def open_template_editor(self):
        from .ui.block_editor import BlockEditor
        if self.template_editor is None or not self.template_editor.window.winfo_exists():
            template = self.active_template.clone() if self.active_template else school_template(
                self.phase_settings(), self.safe_int(self.steal_min, 1)*60,
                self.safe_int(self.steal_limit_sec, 120))
            self.template_editor = BlockEditor(self, template)
        self.template_editor.window.deiconify()
        self.template_editor.window.lift()

    def apply_template(self, template):
        # Compile before touching the current clock: invalid drafts cannot reset it.
        phases = compile_template(template)
        self.pause()
        self.active_template = template.clone()
        self.phases = phases
        self.load_phase(0)
        self.refresh_template_status()

    def use_school_format(self):
        if self.running or self.phase_index or self.remaining_ms != self.current_phase().ms:
            if not messagebox.askyesno("Cambiar formato", "Se reiniciará el debate con el formato escolar. ¿Continuar?", parent=self.root):
                return
        self.pause()
        self.active_template = None
        self.rebuild_phases()
        self.load_phase(0)
        self.refresh_template_status()

    def refresh_template_status(self):
        if hasattr(self, "template_status"):
            name = self.active_template.name if self.active_template else "Escolar (20 turnos)"
            self.template_status.configure(text="Formato activo: " + name)
        for name in ("legacy_favor_entry", "legacy_against_entry"):
            if hasattr(self, name):
                getattr(self, name).state(["disabled"] if self.active_template else ["!disabled"])
        if hasattr(self, "legacy_time_frame"):
            for widget in self.legacy_time_frame.winfo_children():
                if hasattr(widget, "state"):
                    widget.state(["disabled"] if self.active_template else ["!disabled"])
