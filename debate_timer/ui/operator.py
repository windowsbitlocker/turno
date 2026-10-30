"""Operator window, navigation, controls, and responsive layout."""
import tkinter as tk
from tkinter import ttk


class OperatorPanelMixin:
    def build_control_window(self):
        header = tk.Frame(self.root, bg=self.BG)
        header.pack(fill="x", padx=32, pady=(16, 0))
        tk.Label(header, text="Temporizador de debate", font=("Segoe UI", 15, "bold"),
                 bg=self.BG, fg=self.TEXT_DARK).pack(anchor="w")
        tabs = tk.Frame(header, bg=self.BG)
        tabs.pack(fill="x", pady=(10, 0))
        self.debate_nav = tk.Button(
            tabs, text="Debate", command=lambda: self.notebook.select(0),
            relief="flat", borderwidth=0, bg=self.BG, activebackground=self.BG,
            cursor="hand2", padx=0, pady=8, takefocus=True)
        self.debate_nav.pack(side="left", padx=(0, 24))
        self.settings_nav = tk.Button(
            tabs, text="Configuración", command=lambda: self.notebook.select(1),
            relief="flat", borderwidth=0, bg=self.BG, activebackground=self.BG,
            cursor="hand2", padx=0, pady=8, takefocus=True)
        self.settings_nav.pack(side="left")
        tk.Frame(self.root, bg=self.BORDER, height=1).pack(fill="x", padx=32)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)
        self.main_tab = ttk.Frame(self.notebook)
        settings_page = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="Debate")
        self.notebook.add(settings_page, text="Configuración")

        # Solo la configuración necesita desplazamiento; el reloj siempre está a mano.
        self.control_canvas = tk.Canvas(settings_page, bg=self.BG, highlightthickness=0)
        self.control_scrollbar = ttk.Scrollbar(settings_page, orient="vertical",
                                               command=self.control_canvas.yview)
        self.control_scrollbar.pack(side="right", fill="y")
        self.control_canvas.pack(side="left", fill="both", expand=True)
        self.control_canvas.configure(yscrollcommand=self.control_scrollbar.set)
        self.advanced_tab = ttk.Frame(self.control_canvas)
        self.canvas_window_id = self.control_canvas.create_window(
            (0, 0), window=self.advanced_tab, anchor="nw")
        self.advanced_tab.bind("<Configure>", lambda event: self.control_canvas.configure(
            scrollregion=self.control_canvas.bbox("all")))
        self.control_canvas.bind("<Configure>", lambda event: self.control_canvas.itemconfigure(
            self.canvas_window_id, width=event.width))

        def scroll_settings(event):
            if self.notebook.index(self.notebook.select()) == 1:
                direction = -3 if getattr(event, "num", None) == 4 else 3
                if getattr(event, "delta", 0):
                    direction = -int(event.delta / 120) or (-1 if event.delta > 0 else 1)
                self.control_canvas.yview_scroll(direction, "units")
        self.root.bind("<MouseWheel>", scroll_settings)
        self.root.bind("<Button-4>", scroll_settings)
        self.root.bind("<Button-5>", scroll_settings)
        self.build_main_tab()
        self.build_advanced_tab()
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        self.root.after_idle(self._on_tab_changed)

    def _on_tab_changed(self, event=None):
        selected = self.notebook.index(self.notebook.select())
        for index, button in enumerate((self.debate_nav, self.settings_nav)):
            self.configure_auto_size(button, fg=self.ACCENT if index == selected else self.TEXT_SOFT,
                             font=("Segoe UI", 10, "bold" if index == selected else "normal"))

    def build_main_tab(self):
        panel = tk.Frame(self.main_tab, bg=self.BG)
        panel.pack(fill="both", expand=True, padx=32, pady=(16, 12))
        panel.columnconfigure(0, weight=1)
        panel.rowconfigure(1, weight=1)
        self.turn_label = tk.Label(panel, text="", bg=self.BG, fg=self.TEXT_SOFT,
                                   font=("Segoe UI", 9), anchor="w")
        self.turn_label.grid(row=0, column=0, sticky="ew")

        hero = tk.Frame(panel, bg=self.BG)
        self.hero = hero
        hero.grid(row=1, column=0, sticky="ew", pady=(10, 12))
        self.current_phase_label = tk.Label(hero, text="", font=("Segoe UI", 21),
                                            bg=self.BG, fg=self.TEXT_DARK)
        self.current_phase_label.pack()
        self.current_team_label = tk.Label(hero, text="", font=("Segoe UI", 12),
                                           bg=self.BG, fg=self.TEXT_SOFT)
        self.current_team_label.pack(pady=(4, 0))
        self.current_time_label = tk.Label(hero, text="", font=("Segoe UI", 76),
                                           bg=self.BG, fg=self.TEXT_DARK)
        self.current_time_label.pack(pady=(0, 0))
        self.status_label = tk.Label(hero, text="Listo", font=("Segoe UI", 10),
                                     bg=self.BG, fg=self.TEXT_SOFT)
        self.status_label.pack(pady=(0, 8))
        self.start_pause_button = self.make_button(
            hero, "Iniciar", self.toggle_timer, "Transport.TButton")
        self.start_pause_button.configure(width=18)
        self.start_pause_button.pack()

        adjustments = tk.Frame(panel, bg=self.BG)
        self.adjustments = adjustments
        adjustments.grid(row=2, column=0, sticky="ew", pady=(0, 18))
        self.make_button(adjustments, "−10 s", lambda: self.adjust_time(-10_000),
                         "Quiet.TButton").pack(side="left")
        self.make_button(adjustments, "+10 s", lambda: self.adjust_time(10_000),
                         "Quiet.TButton").pack(side="left", padx=(6, 0))
        self.make_button(adjustments, "Reiniciar turno", self.reset_current,
                         "Quiet.TButton").pack(side="right")

        self.steal_panel = tk.Frame(panel, bg="#f3f6f9", padx=12, pady=10)
        self.steal_panel.columnconfigure(0, weight=1)
        tk.Label(self.steal_panel, text="Robo / refutación", bg="#f3f6f9",
                 fg=self.TEXT_DARK, font=("Segoe UI", 10, "bold")).grid(
                     row=0, column=0, sticky="w")
        self.robo_status_label = tk.Label(
            self.steal_panel, text="", bg="#f3f6f9", fg=self.TEXT_SOFT,
            font=("Segoe UI", 9), justify="left", anchor="w")
        self.robo_status_label.grid(row=1, column=0, sticky="ew", pady=(5, 0))
        self.steal_button = self.make_button(self.steal_panel, "Iniciar robo", self.start_steal)
        self.steal_button.grid(row=0, column=1, rowspan=2, sticky="e", padx=(12, 0))
        self.end_steal_button = self.make_button(self.steal_panel, "Terminar robo", self.end_steal_now)
        self.end_steal_button.grid(row=0, column=1, rowspan=2, sticky="e", padx=(12, 0))

        navigation = tk.Frame(panel, bg=self.BG)
        navigation.grid(row=4, column=0, sticky="ew")
        navigation.columnconfigure(0, weight=1)
        navigation.columnconfigure(1, weight=1)
        tk.Frame(navigation, bg=self.BORDER, height=1).grid(
            row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        self.previous_button = self.make_button(navigation, "←  Anterior", self.previous_phase,
                                                "Quiet.TButton")
        self.previous_button.grid(row=1, column=0, sticky="w")
        self.next_button = self.make_button(navigation, "Siguiente  →", self.next_phase,
                                            "Quiet.TButton")
        self.next_button.grid(row=1, column=1, sticky="e")
        self.up_next_heading = tk.Label(navigation, text="A CONTINUACIÓN", bg=self.BG,
                                        fg=self.TEXT_SOFT, font=("Segoe UI", 8))
        self.up_next_heading.grid(row=2, column=0, columnspan=2, sticky="w", pady=(10, 4))
        self.up_next_label = tk.Label(navigation, text="", bg=self.BG, fg=self.TEXT_DARK,
                                       font=("Segoe UI", 10), anchor="w", justify="left")
        self.up_next_label.grid(row=3, column=0, columnspan=2, sticky="ew")

        footer = tk.Frame(panel, bg=self.BG)
        footer.grid(row=5, column=0, sticky="ew", pady=(18, 0))
        self.make_button(footer, "Limpiar proyección", self.blank_display,
                         "Quiet.TButton").pack(side="left")
        self.shortcut_note = tk.Label(footer, text="Espacio: iniciar / pausar", bg=self.BG,
                                     fg=self.TEXT_SOFT, font=("Segoe UI", 8))
        self.shortcut_note.pack(side="right")
        panel.bind("<Configure>", self.resize_controls)

    def resize_controls(self, event=None):
        if event is None:
            return
        width = max(300, event.width)
        compact = event.height < 610
        self.hero.grid_configure(pady=(2, 4) if compact else (10, 12))
        self.adjustments.grid_configure(pady=(0, 8) if compact else (0, 18))
        self.configure_auto_size(self.current_time_label, font=("Segoe UI", 44 if compact else 66))
        self.configure_auto_size(self.current_phase_label, font=("Segoe UI", 17 if compact else 21),
                                           wraplength=width - 8)
        for label in (self.current_team_label, self.up_next_label):
            self.configure_auto_size(label, wraplength=width - 28)
        self.configure_auto_size(self.robo_status_label, wraplength=max(160, width - 190))
        # En pantallas bajas se priorizan reloj y botones sobre la vista previa.
        if compact:
            self.up_next_heading.grid_remove()
            self.up_next_label.grid_remove()
        else:
            self.up_next_heading.grid()
            self.up_next_label.grid()
        if width < 470:
            self.shortcut_note.pack_forget()
        elif not self.shortcut_note.winfo_manager():
            self.shortcut_note.pack(side="right")
