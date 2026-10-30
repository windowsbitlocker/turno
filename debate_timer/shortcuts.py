"""Keyboard shortcuts and their focus guards."""
import tkinter as tk
from tkinter import ttk


class ShortcutMixin:
    def bind_shortcuts(self):
        def shortcut(event, action):
            # Escribir en configuración no debe poner en marcha el debate.
            if isinstance(event.widget, (tk.Entry, ttk.Entry, ttk.Spinbox, tk.Text)):
                return
            if event.keysym == "space" and isinstance(event.widget, (tk.Button, ttk.Button)):
                return
            action()
            return "break"

        self.root.bind("<space>", lambda event: shortcut(event, self.toggle_timer))
        self.root.bind("<Right>", lambda event: shortcut(event, self.next_phase))
        self.root.bind("<Left>", lambda event: shortcut(event, self.previous_phase))
        self.root.bind("<Escape>", lambda event: self.pause())
        self.display_fullscreen = False
        self.display.bind("<F11>", self.toggle_display_fullscreen)
        self.display.bind("<Escape>", lambda event: self.set_display_fullscreen(False))

    def toggle_timer(self):
        if self.running:
            self.pause()
        else:
            self.start()
