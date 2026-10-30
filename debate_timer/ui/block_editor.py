"""Visual, data-only debate blocks with drag ordering and nested repeat groups."""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from ..formatting import format_time
from ..storage import load_config, save_config
from ..templates import (DebateTemplate, StageBlock, RepeatBlock, Robo, Team, KINDS,
                         compile_template, school_template, quick_template,
                         template_from_dict, template_to_dict, find_block,
                         move_block, duplicate_block, new_id)

COLORS = {"preparation": "#68836d", "speech": "#426483", "questions": "#746b91",
          "answer": "#527d85", "conclusion": "#866c61", "break": "#7b8187", "jury": "#76754f"}


def parse_duration(value):
    parts = value.strip().split(":")
    if len(parts) == 1:
        seconds = int(parts[0])
    elif len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit() and int(parts[1]) < 60:
        seconds = int(parts[0])*60 + int(parts[1])
    else:
        raise ValueError("Escribe la duración como minutos:segundos o como segundos.")
    if not 1 <= seconds <= 86400:
        raise ValueError("La duración debe estar entre 1 segundo y 24 horas.")
    return seconds


def duration_text(seconds):
    return f"{seconds//60:02d}:{seconds%60:02d}"


class BlockEditor:
    def __init__(self, app, template):
        self.app = app
        self.draft = template.clone()
        self.selected = None
        self.undo_stack, self.redo_stack = [], []
        self.rows = []
        self.drag = None
        self.fields = {}
        self.window = tk.Toplevel(app.root)
        self.window.title("Turno · Editor de bloques")
        self.window.geometry(f"{min(1160, app.root.winfo_screenwidth()-60)}x{min(780, app.root.winfo_screenheight()-100)}")
        self.window.minsize(860, 560)
        self.window.configure(bg=app.BG)
        self.window.protocol("WM_DELETE_WINDOW", self.window.withdraw)
        self.name = tk.StringVar(value=self.draft.name)
        self.build_ui()
        self.draw()
        self.show_properties()

    def button(self, parent, **options):
        options.setdefault("style", "Soft.TButton")
        return ttk.Button(parent, **options)

    def build_ui(self):
        header = tk.Frame(self.window, bg=self.app.BG, padx=20, pady=14)
        header.pack(fill="x")
        tk.Label(header, text="Constructor de debate", font=("Segoe UI", 18),
                 bg=self.app.BG, fg=self.app.TEXT_DARK).pack(anchor="w")
        tk.Label(header, text="Añade bloques, arrástralos para ordenar y ajusta sus propiedades. El reloj actual no cambia hasta aplicar.",
                 bg=self.app.BG, fg=self.app.TEXT_SOFT, wraplength=950, justify="left").pack(anchor="w", pady=(3, 10))
        line = tk.Frame(header, bg=self.app.BG)
        line.pack(fill="x")
        tk.Label(line, text="Formato", bg=self.app.BG).pack(side="left", padx=(0, 8))
        ttk.Entry(line, textvariable=self.name, width=30).pack(side="left", fill="x", expand=True)
        for label, command in (("Equipos…", self.edit_teams), ("Abrir…", self.open_file), ("Guardar…", self.save_file)):
            self.button(line, text=label, command=command).pack(side="left", padx=(8, 0))

        panes = ttk.Panedwindow(self.window, orient="horizontal")
        panes.pack(fill="both", expand=True, padx=20)
        palette = tk.Frame(panes, bg=self.app.BG, width=160)
        board = tk.Frame(panes, bg="#f3f5f7")
        inspector = tk.Frame(panes, bg=self.app.BG, width=310)
        panes.add(palette, weight=0)
        panes.add(board, weight=1)
        panes.add(inspector, weight=0)
        tk.Label(palette, text="BLOQUES", bg=self.app.BG, fg=self.app.TEXT_SOFT,
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(8, 12))
        for kind, label in KINDS.items():
            self.button(palette, text="+ " + label, command=lambda k=kind: self.add_stage(k)).pack(fill="x", pady=3, padx=(0, 12))
        self.button(palette, text="+ Repetir…", command=self.add_repeat).pack(fill="x", pady=(12, 3), padx=(0, 12))
        ttk.Separator(palette).pack(fill="x", pady=14, padx=(0, 12))
        tk.Label(palette, text="PUNTO DE PARTIDA", bg=self.app.BG, fg=self.app.TEXT_SOFT,
                 font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 6))
        for label, factory in (("Escolar", school_template), ("Temporizador simple", quick_template), ("En blanco", DebateTemplate)):
            self.button(palette, text=label, command=lambda f=factory: self.replace_draft(f())).pack(fill="x", pady=3, padx=(0, 12))
        self.canvas = tk.Canvas(board, bg="#f3f5f7", highlightthickness=0, yscrollincrement=20)
        scrollbar = ttk.Scrollbar(board, orient="vertical", command=self.canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.bind("<Configure>", lambda event: self.draw())
        self.canvas.bind("<ButtonPress-1>", self.press)
        self.canvas.bind("<B1-Motion>", self.motion)
        self.canvas.bind("<ButtonRelease-1>", self.release)
        self.canvas.bind("<MouseWheel>", lambda event: self.canvas.yview_scroll(-int(event.delta/120) or (-1 if event.delta > 0 else 1), "units"))
        self.canvas.bind("<Button-4>", lambda event: self.canvas.yview_scroll(-2, "units"))
        self.canvas.bind("<Button-5>", lambda event: self.canvas.yview_scroll(2, "units"))

        tk.Label(inspector, text="PROPIEDADES", bg=self.app.BG, fg=self.app.TEXT_SOFT,
                 font=("Segoe UI", 9)).pack(anchor="w", padx=(14, 0), pady=8)
        properties_canvas = tk.Canvas(inspector, bg=self.app.BG, highlightthickness=0, width=285)
        self.properties_canvas = properties_canvas
        properties_scroll = ttk.Scrollbar(inspector, orient="vertical", command=properties_canvas.yview)
        properties_scroll.pack(side="right", fill="y")
        properties_canvas.pack(fill="both", expand=True, padx=(14, 0))
        properties_canvas.configure(yscrollcommand=properties_scroll.set)
        self.properties = tk.Frame(properties_canvas, bg=self.app.BG)
        item = properties_canvas.create_window((0, 0), window=self.properties, anchor="nw")
        properties_canvas.bind("<Configure>", lambda event: properties_canvas.itemconfigure(item, width=event.width))
        self.properties.bind("<Configure>", lambda event: properties_canvas.configure(scrollregion=properties_canvas.bbox("all")))
        self.window.bind("<MouseWheel>", self.scroll_properties)
        self.window.bind("<Button-4>", self.scroll_properties)
        self.window.bind("<Button-5>", self.scroll_properties)

        tools = tk.Frame(self.window, bg=self.app.BG)
        tools.pack(fill="x", padx=20, pady=(10, 0))
        for label, command in (("↑", lambda: self.nudge(-1)), ("↓", lambda: self.nudge(1)),
                               ("Duplicar", self.duplicate), ("Quitar", self.remove),
                               ("Deshacer", self.undo), ("Rehacer", self.redo)):
            self.button(tools, text=label, command=command).pack(side="left", padx=(0, 6))
        footer = tk.Frame(self.window, bg=self.app.BG)
        footer.pack(fill="x", padx=20, pady=(10, 16))
        self.summary = tk.Label(footer, text="", bg=self.app.BG, fg=self.app.TEXT_SOFT, wraplength=650, justify="left")
        self.summary.pack(side="left", fill="x", expand=True)
        self.button(footer, text="Aplicar al debate", command=self.apply, style="Primary.TButton").pack(side="right")

    def scroll_properties(self, event):
        widget = event.widget
        while widget is not None and widget is not self.window:
            if widget is self.properties_canvas:
                number = getattr(event, "num", None)
                delta = getattr(event, "delta", 0)
                direction = -2 if number == 4 else 2 if number == 5 else -int(delta/120) or (-1 if delta > 0 else 1)
                self.properties_canvas.yview_scroll(direction, "units")
                return "break"
            widget = getattr(widget, "master", None)

    def remember(self):
        self.undo_stack.append(self.draft.clone())
        self.undo_stack = self.undo_stack[-50:]
        self.redo_stack.clear()

    def block(self):
        found = find_block(self.draft, self.selected) if self.selected else None
        return found[0][found[1]] if found else None

    def field(self, key, label, value, choices=None, boolean=False):
        if boolean:
            var = tk.BooleanVar(value=value)
            control = ttk.Checkbutton(self.properties, text=label, variable=var)
        else:
            tk.Label(self.properties, text=label, bg=self.app.BG, fg=self.app.TEXT_SOFT,
                     anchor="w", wraplength=250, justify="left").pack(fill="x", pady=(8, 3))
            var = tk.StringVar(value=value)
            control = ttk.Combobox(self.properties, textvariable=var, values=choices, state="readonly") if choices is not None else ttk.Entry(self.properties, textvariable=var)
        control.pack(fill="x", pady=(3, 0))
        self.fields[key] = var

    def show_properties(self):
        for child in self.properties.winfo_children():
            child.destroy()
        self.fields = {}
        block = self.block()
        if block is None:
            tk.Label(self.properties, text="Selecciona un bloque para editarlo.\n\nAl seleccionar Repetir, los nuevos\nbloques se añaden dentro del grupo.",
                     bg=self.app.BG, fg=self.app.TEXT_SOFT, justify="left").pack(anchor="w", pady=14)
            return
        if isinstance(block, RepeatBlock):
            self.field("count", "Número de repeticiones (1–20)", block.count)
            tk.Label(self.properties, text="Selecciona este grupo y añade bloques\ndesde la columna izquierda, o arrástralos\nsobre su cabecera para introducirlos.",
                     bg=self.app.BG, fg=self.app.TEXT_SOFT, justify="left").pack(anchor="w", pady=12)
        else:
            self.field("name", "Nombre de la etapa", block.name)
            self.field("kind", "Tipo de bloque", KINDS[block.kind], list(KINDS.values()))
            self.team_choices = {"Sin equipo / compartido": None}
            self.team_choices.update({f"{index+1}. {team.name}": team.id for index, team in enumerate(self.draft.teams)})
            self.field("team_id", "Equipo que habla", next((name for name, identity in self.team_choices.items() if identity == block.team_id), "Sin equipo / compartido"), list(self.team_choices))
            self.field("role", "Rol opcional (pregunta, responde…)", block.role)
            self.field("shared_label", "Texto si no hay equipo (Todos, Jurado…)", block.shared_label)
            self.field("seconds", "Duración (mm:ss o segundos)", duration_text(block.seconds))
            self.field("warning_seconds", "Aviso: segundos restantes (0 = sin aviso)", block.warning_seconds)
            self.field("robo_on", "Permitir robo en este bloque", bool(block.robo), boolean=True)
            robo_names = {name: identity for name, identity in self.team_choices.items() if identity is not None}
            fallback = next((name for name, identity in robo_names.items() if identity != block.team_id), "")
            selected = next((name for name, identity in robo_names.items() if block.robo and identity == block.robo.team_id), fallback)
            self.field("robo_team", "Equipo autorizado para el robo", selected, list(robo_names))
            self.field("robo_seconds", "Duración máxima del robo (mm:ss)", duration_text(block.robo.seconds if block.robo else 60))
            self.field("robo_window", "Permitir solicitud durante los primeros (mm:ss)", duration_text(block.robo.window_seconds if block.robo else min(120, max(1, block.seconds))))
            self.field("robo_deduct", "Descontar del tiempo de esta etapa", block.robo.deduct if block.robo else True, boolean=True)
        self.button(self.properties, text="Guardar cambios del bloque", command=self.save_block).pack(fill="x", pady=16)

    def commit_form(self):
        try:
            name = self.name.get().strip()
            if not name or len(name) > 200:
                raise ValueError("Escribe un nombre de formato de hasta 200 caracteres.")
            block = self.block()
            replacement = duplicate_block(block) if block else None
            if replacement:
                replacement.id = block.id
                if isinstance(replacement, RepeatBlock):
                    # Preserve children and their identities; only the count is edited.
                    replacement.blocks = block.blocks
                    replacement.count = int(self.fields["count"].get())
                    if not 1 <= replacement.count <= 20:
                        raise ValueError("La repetición debe estar entre 1 y 20.")
                else:
                    replacement.name = self.fields["name"].get().strip()
                    replacement.kind = next(key for key, value in KINDS.items() if value == self.fields["kind"].get())
                    replacement.team_id = self.team_choices[self.fields["team_id"].get()]
                    replacement.role = self.fields["role"].get().strip()
                    replacement.shared_label = self.fields["shared_label"].get().strip()
                    replacement.seconds = parse_duration(self.fields["seconds"].get())
                    replacement.warning_seconds = int(self.fields["warning_seconds"].get())
                    replacement.robo = None
                    if self.fields["robo_on"].get():
                        team_id = self.team_choices.get(self.fields["robo_team"].get())
                        replacement.robo = Robo(team_id, parse_duration(self.fields["robo_seconds"].get()),
                            parse_duration(self.fields["robo_window"].get()), self.fields["robo_deduct"].get())
                    # Validate the properties in a single-stage template; other groups may be drafts.
                    compile_template(DebateTemplate(name, self.draft.teams, [replacement]))
            if self.draft.name != name or replacement != block:
                self.remember()
                self.draft.name = name
                if block:
                    siblings, index, _ = find_block(self.draft, block.id)
                    siblings[index] = replacement
            return True
        except (ValueError, KeyError, StopIteration) as error:
            messagebox.showerror("Revisa el bloque", str(error) or "Propiedad no válida.", parent=self.window)
            return False

    def save_block(self):
        if self.commit_form():
            self.draw()

    def select(self, identity):
        if identity == self.selected:
            return True
        if not self.commit_form():
            return False
        self.selected = identity
        self.show_properties()
        self.draw()
        return True

    def insert(self, block):
        if not self.commit_form():
            return
        self.remember()
        current = self.block()
        if isinstance(current, RepeatBlock):
            current.blocks.append(block)
        elif current:
            siblings, index, _ = find_block(self.draft, current.id)
            siblings.insert(index+1, block)
        else:
            self.draft.blocks.append(block)
        self.selected = block.id
        self.show_properties()
        self.draw()

    def add_stage(self, kind):
        seconds = 40 if kind == "questions" else 60 if kind in ("answer", "preparation", "break") else 300 if kind == "jury" else 180
        self.insert(StageBlock(KINDS[kind], kind, self.draft.teams[0].id if self.draft.teams and kind not in ("preparation", "break", "jury") else None,
                               seconds, min(30, seconds), shared_label="Jurado" if kind == "jury" else "Ambos equipos"))

    def add_repeat(self):
        self.insert(RepeatBlock())

    def duplicate(self):
        if self.block():
            if self.commit_form():
                self.insert(duplicate_block(self.block()))

    def remove(self):
        block = self.block()
        if block:
            self.remember()
            siblings, index, _ = find_block(self.draft, block.id)
            siblings.pop(index)
            self.selected = None
            self.show_properties()
            self.draw()

    def nudge(self, delta):
        if not self.block() or not self.commit_form():
            return
        siblings, index, ancestors = find_block(self.draft, self.selected)
        if not 0 <= index+delta < len(siblings):
            return
        self.remember()
        move_block(self.draft, self.selected, ancestors[-1] if ancestors else None, index-1 if delta < 0 else index+2)
        self.draw()

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.draft.clone())
            self.draft = self.undo_stack.pop()
            self.after_history()

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(self.draft.clone())
            self.draft = self.redo_stack.pop()
            self.after_history()

    def after_history(self):
        self.name.set(self.draft.name)
        if not self.block():
            self.selected = None
        self.show_properties()
        self.draw()

    def replace_draft(self, template):
        if not messagebox.askyesno("Cambiar borrador", "¿Reemplazar el borrador del editor? El debate activo no cambiará.", parent=self.window):
            return
        self.remember()
        self.draft = template
        self.selected = None
        self.name.set(template.name)
        self.show_properties()
        self.draw()

    def draw(self):
        if not hasattr(self, "canvas"):
            return
        self.canvas.delete("all")
        self.rows = []
        width = max(250, self.canvas.winfo_width())
        names = {team.id: team.name for team in self.draft.teams}
        def blocks(values, parent=None, depth=0, y=18):
            left, right = 12+min(depth, 8)*18, width-12
            for index, block in enumerate(values):
                top = y
                repeat = isinstance(block, RepeatBlock)
                color = "#9b8653" if repeat else COLORS.get(block.kind, "#426483")
                selected = block.id == self.selected
                self.canvas.create_rectangle(left, y, right, y+64, fill="white", outline=self.app.ACCENT if selected else "#dce2e8", width=2 if selected else 1)
                self.canvas.create_rectangle(left, y, left+5, y+64, fill=color, outline=color)
                self.canvas.create_text(left+18, y+30, text="⋮", fill="#7c8790", font=("Segoe UI", 16))
                heading = f"Repetir {block.count} veces" if repeat else block.name
                self.canvas.create_text(left+34, y+18, anchor="w", text=heading[:42], font=("Segoe UI", 10, "bold"), fill=self.app.TEXT_DARK)
                detail = "Arrastra bloques aquí o añádelos al seleccionar el grupo" if repeat else f"{names.get(block.team_id, block.shared_label or 'Todos')} · {duration_text(block.seconds)}" + (" · Robo" if block.robo else "")
                self.canvas.create_text(left+34, y+44, anchor="w", text=detail[:60], font=("Segoe UI", 9), fill=self.app.TEXT_SOFT)
                self.rows.append(dict(id=block.id, parent=parent, index=index, top=y, bottom=y+64, left=left, repeat=repeat, end=False))
                y += 72
                if repeat:
                    if block.blocks:
                        y = blocks(block.blocks, block.id, depth+1, y)
                    else:
                        self.canvas.create_text(left+36, y+12, text="Grupo vacío · añade una etapa", anchor="w", fill="#8e846e")
                        y += 30
                    self.canvas.create_rectangle(left+18, y, right, y+24, fill="#f4f0e7", outline="")
                    self.canvas.create_text(left+32, y+12, text="Fin de repetición", anchor="w", fill="#8e846e", font=("Segoe UI", 8))
                    self.rows.append(dict(id=block.id, parent=block.id, index=len(block.blocks), top=y, bottom=y+24, left=left+18, repeat=True, end=True))
                    y += 36
            return y
        bottom = blocks(self.draft.blocks)
        if not self.draft.blocks:
            self.canvas.create_text(24, 40, anchor="nw", text="Tu debate comienza aquí.\nAñade una etapa desde la izquierda.", fill=self.app.TEXT_SOFT, font=("Segoe UI", 12))
            bottom = 150
        self.canvas.configure(scrollregion=(0, 0, width, bottom+20))
        try:
            phases = compile_template(self.draft)
            self.summary.configure(text=f"{len(phases)} turnos · Duración base: {format_time(sum(p.ms for p in phases), False)} · Los robos sin descuento pueden añadir tiempo.")
        except ValueError as error:
            self.summary.configure(text="Borrador: " + str(error))

    def hit(self, y):
        return next((row for row in self.rows if row["top"] <= y <= row["bottom"]), None)

    def press(self, event):
        row = self.hit(self.canvas.canvasy(event.y))
        if row and self.select(row["id"]):
            self.drag = (row["id"], event.x, event.y)

    def motion(self, event):
        if not self.drag or abs(event.y-self.drag[2])+abs(event.x-self.drag[1]) < 6:
            return
        if event.y > self.canvas.winfo_height()-30:
            self.canvas.yview_scroll(1, "units")
        elif event.y < 30:
            self.canvas.yview_scroll(-1, "units")
        self.canvas.delete("drop")
        y = self.canvas.canvasy(event.y)
        row = self.hit(y)
        if row:
            inside = row["repeat"] and (row["end"] or event.x > row["left"]+30)
            self.canvas.create_line(row["left"]+(18 if inside else 0), row["top"], max(250, self.canvas.winfo_width())-12,
                                    row["top"], fill=self.app.ACCENT, width=3, tags="drop")

    def release(self, event):
        drag, self.drag = self.drag, None
        self.canvas.delete("drop")
        if not drag or abs(event.y-drag[2])+abs(event.x-drag[1]) < 6:
            return
        row = self.hit(self.canvas.canvasy(event.y))
        if row and row["id"] == drag[0]:
            return
        candidate = self.draft.clone()
        try:
            if row and row["repeat"] and (row["end"] or event.x > row["left"]+30):
                move_block(candidate, drag[0], row["id"], None if row["end"] else 0)
            elif row:
                move_block(candidate, drag[0], row["parent"], row["index"])
            else:
                move_block(candidate, drag[0])
        except ValueError as error:
            messagebox.showerror("No se puede mover", str(error), parent=self.window)
            return
        self.remember()
        self.draft = candidate
        self.draw()

    def open_file(self):
        path = filedialog.askopenfilename(title="Abrir plantilla de bloques", filetypes=[("Plantilla Turno", "*.json")], parent=self.window)
        if path:
            try:
                template = template_from_dict(load_config(path))
                self.replace_draft(template)
            except (ValueError, OSError) as error:
                messagebox.showerror("No se pudo abrir", str(error), parent=self.window)

    def save_file(self):
        if not self.commit_form():
            return
        try:
            data = template_to_dict(self.draft)
        except ValueError as error:
            messagebox.showerror("Revisa el formato", str(error), parent=self.window)
            return
        path = filedialog.asksaveasfilename(title="Guardar plantilla", defaultextension=".json", filetypes=[("Plantilla Turno", "*.json")], parent=self.window)
        if path:
            try:
                save_config(path, data)
            except OSError as error:
                messagebox.showerror("No se pudo guardar", str(error), parent=self.window)

    def apply(self):
        if not self.commit_form():
            return
        try:
            compile_template(self.draft)
        except ValueError as error:
            messagebox.showerror("Revisa el formato", str(error), parent=self.window)
            return
        if not messagebox.askyesno("Aplicar formato", "Se pausará y reiniciará el debate desde el primer bloque. ¿Aplicar?", parent=self.window):
            return
        self.app.apply_template(self.draft)
        self.summary.configure(text="Formato aplicado. Inicia el primer turno desde los controles del operador.")

    def edit_teams(self):
        if not self.commit_form():
            return
        window = tk.Toplevel(self.window)
        window.title("Equipos del formato")
        window.geometry("400x410")
        window.transient(self.window)
        table = ttk.Treeview(window, columns=("name",), show="headings", selectmode="browse")
        table.heading("name", text="Equipo")
        table.pack(fill="both", expand=True, padx=14, pady=14)
        name = tk.StringVar()
        ttk.Entry(window, textvariable=name).pack(fill="x", padx=14)
        def refresh():
            for item in table.get_children(): table.delete(item)
            for team in self.draft.teams: table.insert("", "end", iid=team.id, values=(team.name,))
            self.show_properties()
            self.draw()
        def select(event):
            chosen = table.selection()
            if chosen: name.set(next(team.name for team in self.draft.teams if team.id == chosen[0]))
        table.bind("<<TreeviewSelect>>", select)
        def change(action):
            text = name.get().strip()
            chosen = table.selection()
            if action != "remove" and (not text or len(text) > 200):
                messagebox.showerror("Nombre de equipo", "Escribe un nombre de hasta 200 caracteres.", parent=window)
                return
            if action == "add":
                if len(self.draft.teams) >= 32: return
                self.remember()
                self.draft.teams.append(Team(new_id(), text))
            elif chosen:
                identity = chosen[0]
                if action == "remove":
                    def used(blocks):
                        return any(used(block.blocks) if isinstance(block, RepeatBlock) else block.team_id == identity or (block.robo and block.robo.team_id == identity) for block in blocks)
                    if used(self.draft.blocks):
                        messagebox.showerror("Equipo en uso", "Cambia primero los bloques que usan este equipo.", parent=window)
                        return
                    self.remember()
                    self.draft.teams = [team for team in self.draft.teams if team.id != identity]
                else:
                    self.remember()
                    next(team for team in self.draft.teams if team.id == identity).name = text
            refresh()
        buttons = ttk.Frame(window)
        buttons.pack(fill="x", padx=14, pady=14)
        for text, action in (("Añadir", "add"), ("Renombrar", "rename"), ("Quitar", "remove")):
            self.button(buttons, text=text, command=lambda a=action: change(a)).pack(side="left", padx=3)
        refresh()
