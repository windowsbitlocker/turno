"""Live sizing of projector elements; operator controls keep their normal sizes."""
import tkinter as tk
from tkinter import ttk, font as tkfont
from copy import deepcopy


class SizeEditor:
    def __init__(self, app):
        self.app = app
        self.values = {}
        self.originals = {}
        self.fonts = {}
        self.dialog = None
        self.target = None
        self.rows = []
        self.pending_changes = {}
        self.widgets = {}
        self.register()
        app.display.bind("<Button-3>", self.open_event, add="+")

    def key(self, widget):
        return getattr(widget, "size_key", str(widget))

    def editable(self, widget):
        return widget.winfo_toplevel() is self.app.display and isinstance(widget, tk.Label)

    def register(self):
        def visit(widget):
            if widget is self.dialog:
                return
            if self.editable(widget):
                key = self.key(widget)
                self.widgets[key] = widget
                if key not in self.originals:
                    options = widget.keys()
                    original = {name: widget.cget(name) for name in ("width", "height", "wraplength") if name in options}
                    if "font" in options:
                        original["font"] = widget.cget("font")
                        original["font_actual"] = tkfont.Font(root=self.app.root, font=original["font"]).actual()
                    if isinstance(widget, ttk.Widget):
                        original["style"] = widget.cget("style") or widget.winfo_class()
                        original["font_actual"] = tkfont.Font(root=self.app.root,
                            font=self.app.style.lookup(original["style"], "font") or "TkDefaultFont").actual()
                    manager = widget.winfo_manager()
                    if manager in ("pack", "grid"):
                        original["geometry"] = {name: getattr(widget, manager + "_info")().get(name, 0)
                                                for name in ("padx", "pady")}
                    self.originals[key] = original
            for child in widget.winfo_children():
                visit(child)
        visit(self.app.display)

    def customized(self, widget, option="font_size"):
        return option in self.values.get(self.key(widget), {})

    def apply(self, widget):
        if not self.editable(widget):
            return
        key = self.key(widget)
        values = self.values.get(key, {})
        original = self.originals[key]
        if "font_size" in values and "font_actual" in original:
            font = self.fonts.setdefault(key, tkfont.Font(root=self.app.root, **original["font_actual"]))
            font.configure(size=values["font_size"])
            if isinstance(widget, ttk.Widget):
                style = f"Manual{widget.winfo_id()}.{original['style']}"
                self.app.style.configure(style, font=font)
                widget.configure(style=style)
            else:
                widget.configure(font=font)
        for option in ("width", "height", "wraplength"):
            if option in values and option in widget.keys():
                widget.configure(**{option: values[option]})
        manager = widget.winfo_manager()
        if manager in ("pack", "grid"):
            geometry = {name: values[name] for name in ("padx", "pady") if name in values}
            if geometry:
                getattr(widget, manager + "_configure")(**geometry)

    def set_value(self, widget, option, value):
        if not self.editable(widget):
            raise ValueError("Solo se pueden ajustar elementos del proyector.")
        limits = {"font_size": (6, 360), "width": (0, 150), "height": (0, 12),
                  "wraplength": (0, 4000), "padx": (0, 160), "pady": (0, 160),
                  "logo_size": (20, 600)}
        low, high = limits[option]
        value = max(low, min(high, int(round(float(value)))))
        key = self.key(widget)
        self.values.setdefault(key, {})[option] = value
        if option == "logo_size":
            self.app.load_logos()
            self.target = self.widgets.get(key)
        else:
            self.apply(widget)

    def reset(self, widget):
        key = self.key(widget)
        self.values.pop(key, None)
        if key.startswith("logo:"):
            self.app.load_logos()
            return
        original = self.originals[key]
        for name in ("font", "width", "height", "wraplength", "style"):
            if name in original:
                widget.configure(**{name: original[name]})
        manager = widget.winfo_manager()
        if manager in ("pack", "grid") and "geometry" in original:
            getattr(widget, manager + "_configure")(**original["geometry"])

    def export(self):
        return deepcopy(self.values)

    def restore(self, values):
        self.cancel_pending()
        for key in list(self.values):
            widget = self.widgets.get(key)
            if widget is not None and widget.winfo_exists():
                self.reset(widget)
        self.values = {}
        if not isinstance(values, dict):
            return
        self.register()
        for key, options in values.items():
            widget = self.widgets.get(key)
            if widget is None or not isinstance(options, dict) or not widget.winfo_exists():
                continue
            for option, value in options.items():
                if option in {"font_size", "width", "height", "wraplength", "padx", "pady", "logo_size"}:
                    try:
                        self.set_value(widget, option, value)
                    except (ValueError, TypeError, OverflowError):
                        pass

    def open_event(self, event):
        if self.editable(event.widget):
            self.open(event.widget)
            return "break"

    def open(self, target=None):
        if target is not None and not self.editable(target):
            return
        self.register()
        if self.dialog is None or not self.dialog.winfo_exists():
            self.dialog = tk.Toplevel(self.app.root)
            self.dialog.title("Tamaños del proyector")
            self.dialog.geometry("460x540")
            self.dialog.minsize(360, 420)
            self.dialog.configure(bg=self.app.BG)
            self.dialog.columnconfigure(1, weight=1)
            tk.Label(self.dialog, text="Ajusta el proyector en vivo", bg=self.app.BG,
                     fg=self.app.TEXT_DARK, font=("Segoe UI", 14)).grid(
                         row=0, column=0, columnspan=3, sticky="w", padx=18, pady=(16, 6))
            tk.Label(self.dialog, text="Haz clic derecho en un elemento del proyector.\n"
                     "0 = ancho o ajuste de línea automático.", justify="left",
                     bg=self.app.BG, fg=self.app.TEXT_SOFT).grid(row=1, column=0, columnspan=3,
                                                               sticky="w", padx=18, pady=(0, 12))
            self.selector = ttk.Combobox(self.dialog, state="readonly")
            self.selector.grid(row=2, column=0, columnspan=3, sticky="ew", padx=18, pady=(0, 14))
            self.selector.bind("<<ComboboxSelected>>", lambda event: self.show_target(self.choices[self.selector.current()]))
            self.controls = tk.Frame(self.dialog, bg=self.app.BG)
            self.controls.grid(row=3, column=0, columnspan=3, sticky="ew", padx=18)
            self.controls.columnconfigure(1, weight=1)
            ttk.Button(self.dialog, text="Restaurar este elemento", command=self.reset_target).grid(
                row=4, column=0, columnspan=3, sticky="ew", padx=18, pady=16)
        self.choices = [widget for widget in self.widgets.values() if widget.winfo_exists() and self.editable(widget)]
        labels = []
        names = {self.app.display_title_label: "Título del evento",
                 self.app.display_phase_label: "Etapa del debate",
                 self.app.display_team_label: "Nombre del equipo",
                 self.app.display_timer_label: "Reloj",
                 self.app.display_robo_label: "Avisos / robo"}
        for index, widget in enumerate(self.choices):
            name = names.get(widget, "Logo")
            if self.key(widget).startswith("logo:"):
                name = "Logo"
            labels.append(f"{index+1}. {name}")
        self.selector.configure(values=labels)
        target = target or self.app.display_timer_label
        self.selector.current(self.choices.index(target))
        self.show_target(target)
        self.dialog.deiconify()
        self.dialog.lift()

    def show_target(self, widget):
        self.cancel_pending()
        self.target = widget
        for child in self.controls.winfo_children():
            child.destroy()
        key = self.key(widget)
        original = self.originals[key]
        values = self.values.get(key, {})
        if key.startswith("logo:"):
            options = [("logo_size", "Tamaño del logo (px)", 20, 600, 190)]
        else:
            options = []
            if "font_actual" in original:
                current = tkfont.Font(root=self.app.root, font=widget.cget("font")).actual("size") if "font" in widget.keys() else original["font_actual"]["size"]
                options.append(("font_size", "Texto (puntos)", 6, 360, abs(int(current))))
            for name, label, high in (("width", "Ancho (caracteres)", 150),
                                       ("height", "Alto (líneas)", 12),
                                       ("wraplength", "Ajuste de línea (px)", 4000)):
                if name in original:
                    raw = widget.cget(name)
                    options.append((name, label, 0, high, int(float(raw or 0))))
            if "geometry" in original:
                for name, label in (("padx", "Margen horizontal (px)"), ("pady", "Margen vertical (px)")):
                    raw = getattr(widget, widget.winfo_manager() + "_info")().get(name, 0)
                    parts = widget.tk.splitlist(raw) if isinstance(raw, str) else raw if isinstance(raw, tuple) else (raw,)
                    options.append((name, label, 0, 160, int(parts[0])))
        for row, (option, label, low, high, initial) in enumerate(options):
            tk.Label(self.controls, text=label, bg=self.app.BG, fg=self.app.TEXT_SOFT).grid(
                row=row, column=0, sticky="w", pady=7)
            # Integer-resolution scales avoid fractional values fighting a spinbox's
            # integer variable during a drag. Apply changes after input processing,
            # so resizing the target cannot interrupt the slider's mouse handling.
            variable = tk.StringVar(value=str(values.get(option, initial)))
            scale = tk.Scale(self.controls, from_=low, to=high, variable=variable,
                             orient="horizontal", resolution=1, showvalue=False,
                             length=180, width=18, sliderlength=24,
                             bg=self.app.BG, activebackground="#bccbd8",
                             troughcolor="#e8edf2", highlightthickness=0, bd=0)
            scale.grid(row=row, column=1, sticky="ew", padx=8)
            spin = ttk.Spinbox(self.controls, from_=low, to=high, textvariable=variable, width=6)
            spin.grid(row=row, column=2)
            def changed(*args, var=variable, name=option, target=widget):
                try:
                    value = float(var.get())
                except (tk.TclError, ValueError):
                    return
                key = (self.key(target), name)
                previous = self.pending_changes.pop(key, None)
                if previous:
                    self.app.root.after_cancel(previous)
                def commit():
                    self.pending_changes.pop(key, None)
                    if target.winfo_exists():
                        self.set_value(target, name, value)
                self.pending_changes[key] = self.app.root.after_idle(commit)
            variable.trace_add("write", changed)
            scale.variable_reference = variable

    def cancel_pending(self):
        for callback in self.pending_changes.values():
            self.app.root.after_cancel(callback)
        self.pending_changes.clear()

    def reset_target(self):
        if self.target and self.target.winfo_exists():
            self.cancel_pending()
            key = self.key(self.target)
            self.reset(self.target)
            self.show_target(self.widgets[key])
