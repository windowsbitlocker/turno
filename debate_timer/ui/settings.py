"""Settings form and Tk variables."""
import tkinter as tk
from tkinter import ttk


class SettingsPanelMixin:
    def build_variables(self):
        self.title_var = tk.StringVar(value="Debate de Historia")
        self.team_favor_var = tk.StringVar(value="Equipo a favor")
        self.team_against_var = tk.StringVar(value="Equipo en contra")

        self.prep_min = tk.IntVar(value=1)
        self.opening_min = tk.IntVar(value=3)
        self.question_sec = tk.IntVar(value=40)
        self.answer_min = tk.IntVar(value=1)
        self.final_prep_min = tk.IntVar(value=5)
        self.conclusion_min = tk.IntVar(value=3)
        self.steal_min = tk.IntVar(value=1)
        self.jury_min = tk.IntVar(value=5)

        self.show_milliseconds_var = tk.BooleanVar(value=True)
        self.warning_opening_sec = tk.IntVar(value=30)
        self.warning_short_sec = tk.IntVar(value=10)
        self.warning_jury_sec = tk.IntVar(value=60)
        self.steal_limit_sec = tk.IntVar(value=120)

    def build_advanced_tab(self):
        pad = 8
        LBL = ("Segoe UI", 10)

        info_frame = self.card(self.advanced_tab, "Información del evento")

        tk.Label(info_frame, text="Título", bg=self.CARD_BG, fg=self.TEXT_SOFT, font=LBL).grid(row=0, column=0, sticky="w", padx=pad, pady=4)
        ttk.Entry(info_frame, textvariable=self.title_var, style="Clean.TEntry").grid(row=0, column=1, sticky="ew", padx=pad, pady=4)

        tk.Label(info_frame, text="Equipo a favor", bg=self.CARD_BG, fg=self.TEXT_SOFT, font=LBL).grid(row=1, column=0, sticky="w", padx=pad, pady=4)
        self.legacy_favor_entry = ttk.Entry(info_frame, textvariable=self.team_favor_var, style="Clean.TEntry")
        self.legacy_favor_entry.grid(row=1, column=1, sticky="ew", padx=pad, pady=4)

        tk.Label(info_frame, text="Equipo en contra", bg=self.CARD_BG, fg=self.TEXT_SOFT, font=LBL).grid(row=2, column=0, sticky="w", padx=pad, pady=4)
        self.legacy_against_entry = ttk.Entry(info_frame, textvariable=self.team_against_var, style="Clean.TEntry")
        self.legacy_against_entry.grid(row=2, column=1, sticky="ew", padx=pad, pady=4)

        self.make_button(info_frame, "Elegir logos", self.choose_logos).grid(row=3, column=0, padx=pad, pady=6)
        self.make_button(info_frame, "Aplicar cambios", self.apply_settings, "Primary.TButton").grid(row=3, column=1, sticky="ew", padx=pad, pady=6)
        self.make_button(info_frame, "Quitar logos", self.clear_logos, "Danger.TButton").grid(row=4, column=0, columnspan=2, sticky="ew", padx=pad, pady=(0, 6))
        info_frame.columnconfigure(1, weight=1)

        file_frame = self.card(self.advanced_tab, "Archivo portátil")

        self.make_button(file_frame, "Exportar configuración", self.export_config).pack(side="left", expand=True, fill="x", padx=5, pady=8)
        self.make_button(file_frame, "Importar configuración", self.import_config).pack(side="left", expand=True, fill="x", padx=5, pady=8)

        formats = self.card(self.advanced_tab, "Formato del debate")
        self.template_status = tk.Label(formats, text="Formato activo: Escolar (20 turnos)",
                                        bg=self.BG, fg=self.TEXT_SOFT, anchor="w", wraplength=400)
        self.template_status.pack(fill="x", pady=(0, 8))
        tk.Label(formats, text="Con una plantilla, los equipos, tiempos y avisos se editan en sus bloques.",
                 bg=self.BG, fg=self.TEXT_SOFT, wraplength=400, justify="left").pack(fill="x", pady=(0, 8))
        self.make_button(formats, "Editor por bloques…", self.open_template_editor,
                         "Primary.TButton").pack(fill="x", pady=(0, 8))
        self.make_button(formats, "Volver al formato escolar", self.use_school_format).pack(fill="x")

        times = self.card(self.advanced_tab, "Tiempos del formato escolar")
        self.legacy_time_frame = times

        self.add_time_row(times, "Preparación / espera inicial, minutos", self.prep_min, 0)
        self.add_time_row(times, "Presentación inicial, minutos", self.opening_min, 1)
        self.add_time_row(times, "Pregunta, segundos", self.question_sec, 2)
        self.add_time_row(times, "Respuesta, minutos", self.answer_min, 3)
        self.add_time_row(times, "Preparación final (por equipo), minutos", self.final_prep_min, 4)
        self.add_time_row(times, "Conclusión, minutos", self.conclusion_min, 5)
        self.add_time_row(times, "Robo / refutación, minutos", self.steal_min, 6)
        self.add_time_row(times, "Deliberación del jurado, minutos", self.jury_min, 7)

        self.make_button(
            times,
            "Aplicar tiempos",
            self.apply_settings,
            "Primary.TButton"
        ).grid(row=8, column=0, columnspan=2, sticky="ew", padx=pad, pady=8)

        warnings = self.card(self.advanced_tab, "Avisos y precisión")

        self.add_time_row(warnings, "Mostrar décimas de segundo", self.show_milliseconds_var, 0, is_check=True)
        self.add_time_row(warnings, "Aviso presentación/conclusión, segundos", self.warning_opening_sec, 1)
        self.add_time_row(warnings, "Aviso pregunta/respuesta/robo, segundos", self.warning_short_sec, 2)
        self.add_time_row(warnings, "Aviso jurado, segundos", self.warning_jury_sec, 3)
        self.add_time_row(warnings, "Límite para robo, segundos desde inicio", self.steal_limit_sec, 4)

        self.make_button(
            warnings,
            "Aplicar avisos",
            self.apply_settings,
            "Primary.TButton"
        ).grid(row=5, column=0, columnspan=2, sticky="ew", padx=pad, pady=8)

        self.make_button(self.advanced_tab, "Ajustar tamaños del proyector…",
                         lambda: self.size_editor.open()).pack(fill="x", padx=28, pady=(16, 24))

    def add_time_row(self, parent, text, var, row, is_check=False):
        tk.Label(
            parent,
            text=text,
            bg=self.CARD_BG,
            fg=self.TEXT_SOFT,
            font=("Segoe UI", 10)
        ).grid(row=row, column=0, sticky="w", padx=10, pady=6)

        if is_check:
            ttk.Checkbutton(parent, variable=var).grid(row=row, column=1, sticky="e", padx=10, pady=6)
        else:
            ttk.Spinbox(parent, from_=0, to=600, textvariable=var, width=8, style="Clean.TSpinbox").grid(row=row, column=1, sticky="e", padx=10, pady=6)

        parent.columnconfigure(0, weight=1)
