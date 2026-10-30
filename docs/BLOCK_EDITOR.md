# Visual debate templates

This feature belongs to the **public Turno project**. It does not modify the user's
independent personal timer. It is currently available in the source working copy;
the published Windows v0.1.0 release predates it.

## Open

Run Turno from source, then choose **Configuración → Editor por bloques…**, or run:

```console
python -m debate_timer --edit-template
```

The editor has three areas: the block palette, the ordered debate, and properties
for the selected block. A draft does not pause or change the running debate.

## Build a format

1. Start from **Escolar**, **Temporizador simple**, or **En blanco**.
2. Use **Equipos…** to add or rename teams. A team in use must be removed from its
   blocks before it can be deleted. Team identity is independent of its display name.
3. Add preparation, speech, question, answer, conclusion, break, or jury blocks.
4. Select a block and set its name, speaking team, optional role, duration, and warning.
   Durations accept `mm:ss` or a whole number of seconds. A warning of `0` disables it.
5. Drag blocks to reorder them, or use **↑ / ↓**. **Duplicar**, **Quitar**,
   **Deshacer**, and **Rehacer** support editing the sequence.
6. Add **Repetir…** to repeat a sequence. Select that group before adding child blocks,
   or drag blocks onto its header. Drag onto its footer to append a child. Drop near
   the left edge of a group header to place a block before it instead of inside it.
7. Use **Guardar…** to export a reusable template, or **Abrir…** to load one.
8. Choose **Aplicar al debate** and confirm. This pauses the current clock and starts
   the configured sequence at its first stage, ready for the operator to start it.

Property edits are committed when switching blocks, saving, or applying the template.
**Guardar cambios del bloque** updates the visual card immediately. Closing the editor
hides it and keeps its in-memory draft; save a template file to retain it after closing Turno.

The duration preview includes expanded repeats. It reports base stage time; optional
non-deducting robo time and operator pauses can extend the actual debate.

## Optional robo rules

Robo is disabled unless explicitly enabled for a block. A conclusion does not
automatically enable it in a custom template. Specify:

- Which other team may use it.
- Maximum robo duration.
- How long after the stage begins a request remains available.
- Whether the used time is deducted from the interrupted stage.

Robo remains operator-controlled, once per loaded stage. It pauses the main stage,
uses a separate countdown, then leaves the stage paused for the operator to resume.
With deduction enabled, it is capped by the stage's remaining time. Without deduction,
the stage time is preserved. The existing school format keeps its prior robo rules.

## File format and compatibility

Templates are JSON data, not executable programs. Files identify themselves with
`"format": "turno-template"` and `"version": 1`, plus a template name, teams, and blocks.
Blocks are `stage` or `repeat`; repeats contain child blocks. Unknown schema versions,
invalid teams, duplicate identifiers, invalid durations, and recursive moves are rejected.

Limits: 32 teams, 500 stored blocks, 500 expanded turns, repeat counts from 1 to 20,
and at most 8 nested repeat levels. Stage durations range from 1 second to 24 hours.
The editor does not include an evaluator, arbitrary scripts, conditions, or network features.

The full Turno configuration includes the active template in `plantilla`, alongside
event details, logos, and projector sizes. Legacy configurations without `plantilla`
continue to use the original school format. Invalid template data is validated before
it can reset the current clock or overwrite event settings.

The three starting points are editable examples, not claims of compliance with a
particular tournament's official rules. Verified tournament presets can be added later.
