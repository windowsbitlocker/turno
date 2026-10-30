# Contributing

Use Python 3.10+ with Tkinter. Pillow is optional unless testing logos.

Run `python -B -m unittest discover -s tests -v` before submitting a change. A desktop
is needed for integration tests; the `test_domain.py` suite can run headlessly.

Keep debate sequencing in `phases.py`, countdown operations in `timing.py`, and robo
rules in `rebuttal.py`. Put widget creation and rendering in `ui/`. Keep `models.py`,
`phases.py`, `formatting.py`, and `storage.py` free of Tkinter dependencies.

Preserve Spanish UI strings and the existing JSON field names. Widget creation order
affects persisted projector size identifiers; treat changes to it as configuration
compatibility changes. Update tests and document any such migration.

Do not commit local configurations, school logos/documents, generated archives,
build tools, or private assets. Add a license selected by the owner before public release.
