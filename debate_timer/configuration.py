"""Settings application and backward-compatible JSON import/export."""
from tkinter import filedialog, messagebox
from .storage import load_config, save_config
from .templates import template_from_dict, template_to_dict


class ConfigurationMixin:
    def safe_int(self, var, fallback):
        try:
            return int(var.get())
        except Exception:
            return fallback

    def apply_settings(self):
        old_index = self.phase_index
        self.pause()
        self.rebuild_phases()
        self.load_phase(min(old_index, len(self.phases) - 1))
        self.display_title_label.config(text=self.title_var.get().strip() or "Temporizador de Debate")
        self.load_logos()
        self.refresh_template_status()

    def get_config(self):
        return {
            "titulo": self.title_var.get(),
            "equipo_a_favor": self.team_favor_var.get(),
            "equipo_en_contra": self.team_against_var.get(),
            "logo_paths": self.logo_paths,
            "tamanos_interfaz": self.size_editor.export(),
            "plantilla": template_to_dict(self.active_template) if self.active_template else None,
            "tiempos": {
                "preparacion_min": self.safe_int(self.prep_min, 1),
                "presentacion_min": self.safe_int(self.opening_min, 3),
                "pregunta_sec": self.safe_int(self.question_sec, 40),
                "respuesta_min": self.safe_int(self.answer_min, 1),
                "preparacion_final_min": self.safe_int(self.final_prep_min, 5),
                "conclusion_min": self.safe_int(self.conclusion_min, 3),
                "robo_min": self.safe_int(self.steal_min, 1),
                "jurado_min": self.safe_int(self.jury_min, 5),
            },
            "avanzado": {
                "mostrar_milisegundos": bool(self.show_milliseconds_var.get()),
                "aviso_presentacion_sec": self.safe_int(self.warning_opening_sec, 30),
                "aviso_corto_sec": self.safe_int(self.warning_short_sec, 10),
                "aviso_jurado_sec": self.safe_int(self.warning_jury_sec, 60),
                "limite_robo_sec": self.safe_int(self.steal_limit_sec, 120),
            },
        }

    def apply_config(self, data):
        candidate = template_from_dict(data["plantilla"]) if data.get("plantilla") is not None else None
        self.title_var.set(data.get("titulo", "Debate de Historia"))
        self.team_favor_var.set(data.get("equipo_a_favor", "Equipo a favor"))
        self.team_against_var.set(data.get("equipo_en_contra", "Equipo en contra"))
        logo_paths = data.get("logo_paths")
        if logo_paths is None:
            single = data.get("logo_path")
            logo_paths = [single] if single else []
        self.logo_paths = list(logo_paths)

        tiempos = data.get("tiempos", {})
        self.prep_min.set(tiempos.get("preparacion_min", 1))
        self.opening_min.set(tiempos.get("presentacion_min", 3))
        self.question_sec.set(tiempos.get("pregunta_sec", 40))
        self.answer_min.set(tiempos.get("respuesta_min", 1))
        self.final_prep_min.set(tiempos.get("preparacion_final_min", 5))
        self.conclusion_min.set(tiempos.get("conclusion_min", 3))
        self.steal_min.set(tiempos.get("robo_min", 1))
        self.jury_min.set(tiempos.get("jurado_min", 5))

        avanzado = data.get("avanzado", {})
        self.show_milliseconds_var.set(avanzado.get("mostrar_milisegundos", True))
        self.warning_opening_sec.set(avanzado.get("aviso_presentacion_sec", 30))
        self.warning_short_sec.set(avanzado.get("aviso_corto_sec", 10))
        self.warning_jury_sec.set(avanzado.get("aviso_jurado_sec", 60))
        self.steal_limit_sec.set(avanzado.get("limite_robo_sec", 120))

        self.active_template = candidate
        self.apply_settings()
        self.size_editor.restore(data.get("tamanos_interfaz", {}))

    def export_config(self):
        path = filedialog.asksaveasfilename(
            title="Exportar configuración",
            defaultextension=".json",
            filetypes=[("Configuración JSON", "*.json"), ("Todos los archivos", "*.*")]
        )
        if not path:
            return

        try:
            save_config(path, self.get_config())
            messagebox.showinfo("Exportado", "Configuración exportada correctamente.")
        except Exception as e:
            messagebox.showerror("Error al exportar", str(e))

    def import_config(self):
        path = filedialog.askopenfilename(
            title="Importar configuración",
            filetypes=[("Configuración JSON", "*.json"), ("Todos los archivos", "*.*")]
        )
        if not path:
            return

        try:
            data = load_config(path)
            self.apply_config(data)
            messagebox.showinfo("Importado", "Configuración importada correctamente.")
        except Exception as e:
            messagebox.showerror("Error al importar", str(e))
