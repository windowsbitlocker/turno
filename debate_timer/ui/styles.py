"""Shared colors, typography, and widget helpers."""
import tkinter as tk
from tkinter import ttk


class StyleMixin:
    def setup_styles(self):
        """Colores neutros y jerarquía discreta para el panel de operación."""
        self.BG = "#ffffff"
        self.CARD_BG = "#ffffff"
        self.ACCENT = "#426483"
        self.ACCENT_DARK = "#354f69"
        self.TEXT_DARK = "#222b34"
        self.TEXT_SOFT = "#626c76"
        self.DANGER = "#a33d35"
        self.DANGER_DARK = "#853129"
        self.WARNING = "#e5bd66"
        self.SUCCESS = "#38644c"
        self.BORDER = "#d9dcd9"
        self.root.configure(bg=self.BG)
        self.root.option_add("*Font", ("Segoe UI", 10))

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background=self.BG)
        self.style.layout("TNotebook.Tab", [])
        self.style.configure("Transport.TButton", font=("Segoe UI", 12),
                             padding=(30, 13), background=self.ACCENT,
                             foreground="#ffffff", borderwidth=0, relief="flat",
                             focusthickness=2, focuscolor="#ffffff")
        self.style.map("Transport.TButton",
                       background=[("disabled", "#e8edf1"), ("active", self.ACCENT_DARK)],
                       foreground=[("disabled", "#7d8790")])
        self.style.configure("Quiet.TButton", font=("Segoe UI", 10),
                             padding=(10, 7), background=self.BG,
                             foreground=self.TEXT_SOFT, borderwidth=0, relief="flat")
        self.style.map("Quiet.TButton", background=[("active", "#f1f4f7")],
                       foreground=[("disabled", "#a5adb4"), ("active", self.TEXT_DARK)])
        self.style.configure("TNotebook", background=self.BG, borderwidth=0,
                             bordercolor=self.BG, lightcolor=self.BG, darkcolor=self.BG,
                             tabmargins=(0, 0, 0, 0))
        self.style.configure("TNotebook.Tab", padding=(22, 9),
                             font=("Segoe UI", 10), background=self.BG,
                             foreground=self.TEXT_SOFT, borderwidth=0)
        self.style.map("TNotebook.Tab",
                       background=[("selected", self.CARD_BG), ("active", "#e8eae7")],
                       foreground=[("selected", self.TEXT_DARK)])
        self.style.configure("Card.TLabelframe", background=self.CARD_BG,
                             borderwidth=1, relief="solid", bordercolor=self.BORDER,
                             lightcolor=self.BORDER, darkcolor=self.BORDER,
                             padding=(8, 6))
        self.style.configure("Card.TLabelframe.Label", background=self.BG,
                             foreground=self.TEXT_SOFT, font=("Segoe UI", 10))

        for name, bg, fg, hover in (
            ("Primary.TButton", self.ACCENT, "#ffffff", self.ACCENT_DARK),
            ("Soft.TButton", "#ffffff", self.TEXT_DARK, "#eef0ed"),
            ("Danger.TButton", "#ffffff", self.DANGER, "#f8eeeb"),
        ):
            self.style.configure(name, font=("Segoe UI", 10), padding=(10, 9),
                                 background=bg, foreground=fg, borderwidth=1,
                                 bordercolor=self.BORDER, lightcolor=bg, darkcolor=bg,
                                 relief="flat", focusthickness=2, focuscolor=fg)
            self.style.map(name,
                           background=[("disabled", "#f0f1ee"), ("pressed", hover), ("active", hover)],
                           foreground=[("disabled", "#939a9d")],
                           bordercolor=[("focus", self.ACCENT), ("!focus", self.BORDER)],
                           lightcolor=[("active", hover)], darkcolor=[("active", hover)])

        for name in ("Clean.TEntry", "Clean.TSpinbox"):
            self.style.configure(name, padding=6, fieldbackground="#ffffff",
                                 foreground=self.TEXT_DARK, insertcolor=self.TEXT_DARK,
                                 arrowcolor=self.TEXT_SOFT, background="#f5f6f3",
                                 bordercolor=self.BORDER, lightcolor=self.BORDER,
                                 darkcolor=self.BORDER)
            self.style.map(name, bordercolor=[("focus", self.ACCENT)],
                           lightcolor=[("focus", self.ACCENT)],
                           darkcolor=[("focus", self.ACCENT)])
        self.style.configure("TCheckbutton", background=self.CARD_BG,
                             foreground=self.TEXT_DARK)
        self.style.map("TCheckbutton", background=[("active", self.CARD_BG)],
                       indicatorbackground=[("selected", self.ACCENT)])
        self.style.configure("Vertical.TScrollbar", background="#d5d9d5",
                             troughcolor=self.BG, borderwidth=0, arrowsize=12,
                             arrowcolor=self.TEXT_SOFT)

    def card(self, parent, text):
        # Secciones abiertas: títulos y espacio, sin cajas anidadas.
        section = tk.Frame(parent, bg=self.BG)
        section.pack(fill="x", padx=28, pady=(20, 8))
        tk.Label(section, text=text, bg=self.BG, fg=self.TEXT_DARK,
                 font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 10))
        frame = tk.Frame(section, bg=self.CARD_BG)
        frame.pack(fill="x")
        return frame

    def make_button(self, parent, text, command, style="Soft.TButton"):
        return ttk.Button(parent, text=text, command=command, style=style)
