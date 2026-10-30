"""Audience window, fullscreen behavior, and resizing."""
import tkinter as tk


class ProjectorMixin:
    def toggle_display_fullscreen(self, event=None):
        self.set_display_fullscreen(not self.display_fullscreen)

    def set_display_fullscreen(self, value):
        self.display_fullscreen = value
        try:
            self.display.attributes("-fullscreen", value)
        except Exception:
            pass

    def build_display_window(self):
        self.DISPLAY_BG = "#101820"
        self.display.configure(bg=self.DISPLAY_BG)
        self.display.columnconfigure(0, weight=1)
        self.display.rowconfigure(2, weight=1)
        self.display_logo_frame = tk.Frame(self.display, bg=self.DISPLAY_BG)
        self.display_logo_frame.grid(row=0, column=0, pady=(24, 0))
        self.display_title_label = tk.Label(
            self.display, text="Debate de Historia", font=("Segoe UI", 22),
            bg=self.DISPLAY_BG, fg="#b7c0c8")
        self.display_title_label.grid(row=1, column=0, sticky="ew", padx=28, pady=(12, 8))

        stage = tk.Frame(self.display, bg=self.DISPLAY_BG)
        stage.grid(row=2, column=0, sticky="ew", padx=24, pady=8)
        stage.columnconfigure(0, weight=1)
        self.display_phase_label = tk.Label(
            stage, text="", font=("Segoe UI", 18), bg=self.DISPLAY_BG, fg="#b7c0c8")
        self.display_phase_label.grid(row=0, column=0, sticky="ew")
        self.display_team_label = tk.Label(
            stage, text="", font=("Segoe UI", 28), bg=self.DISPLAY_BG, fg="#ffffff")
        self.display_team_label.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        self.display_timer_label = tk.Label(
            stage, text="00:00.0", font=("Segoe UI", 110), bg=self.DISPLAY_BG, fg="#ffffff")
        self.display_timer_label.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        self.display_robo_label = tk.Label(
            self.display, text="", font=("Segoe UI", 14), bg=self.DISPLAY_BG, fg="#b7c0c8")
        self.display_robo_label.grid(row=3, column=0, sticky="ew", padx=28, pady=(0, 24))
        self.display.bind("<Configure>", self.resize_display)

    def resize_display(self, event=None):
        if event is not None and event.widget is not self.display:
            return
        from tkinter import font as tkfont
        width = max(300, self.display.winfo_width())
        height = max(250, self.display.winfo_height())
        # Limitar por ancho y por alto mantiene el reloj legible en ventanas pequeñas.
        size = max(24, min(126, int(width / 7.8), int(height / 5.8)))
        clock_font = tkfont.Font(family="Segoe UI", size=size)
        while size > 24 and clock_font.measure("00:00.0") > width - 64:
            size -= 1
            clock_font.configure(size=size)
        self.configure_auto_size(self.display_timer_label, font=("Segoe UI", size))
        for label, ratio, minimum, maximum in (
            (self.display_title_label, 0.20, 12, 24),
            (self.display_phase_label, 0.17, 11, 20),
            (self.display_team_label, 0.25, 14, 30),
            (self.display_robo_label, 0.13, 10, 16),
        ):
            self.configure_auto_size(label, font=("Segoe UI", max(minimum, min(maximum, int(size * ratio)))),
                            wraplength=width - 64)

    def blank_display(self):
        self.display_title_label.config(text="")
        self.display_phase_label.config(text="")
        self.display_team_label.config(text="")
        self.display_timer_label.config(text="")
        self.display_robo_label.config(text="")
        for child in self.display_logo_frame.winfo_children():
            child.destroy()
