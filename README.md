# Turno

Turno is an open-source debate timer with a dedicated operator panel and projector display.
Manage speaking turns, preparation periods, and rebuttals, customize event details,
and adjust the display live—all offline.
The interface is in Spanish. Participants do not need electronic devices.

## Windows download

Download the **Windows x64 ZIP** from [GitHub Releases](https://github.com/windowsbitlocker/turno/releases),
extract it, and open **Turno.exe**. Python installation is not needed. The portable
package includes logo support, third-party notices, and the MIT license.

The Windows release targets Windows 10/11 on 64-bit Intel/AMD PCs. It is unsigned.

## Run from source

Requires Python **3.10 or newer** with Tkinter. There are no mandatory third-party
Python dependencies. On Linux, install your distribution's Tkinter package if needed.

```console
python -m debate_timer
```

`python main.py`, the Windows launcher **Iniciar temporizador.cmd**, and the original
`temporizador_debate_v13.py` entry point also work. Importing the package does not
launch the application.

Install optional logo support:

```console
python -m pip install ".[logos]"
```

Or install the package without logo support with `python -m pip install .` and run
`debate-timer`.

## Features

Turno v0.2.0 includes a [visual block editor](docs/BLOCK_EDITOR.md) for custom formats,
teams, per-stage robo rules, and nested repeat blocks. Open **Configuración → Editor
por bloques…**, or run `python -m debate_timer --edit-template` from source.

- Operator and projector windows, including projector fullscreen mode.
- Custom stage sequences, editable teams, durations, warnings, and repeated rounds.
- The original 20-stage school format remains available.
- Start/pause, navigation, reset, and manual time adjustments.
- Operator-controlled robo/refutation during conclusions: only the time used is deducted.
- Manual projector-only sizing: right-click a projector element or use the settings panel.
- JSON configuration import/export, including projector sizing.
- Optional event logos with Pillow. No Bluetooth, web server, or phone application.

See [LEEME.md](LEEME.md) for usage instructions in Spanish.

## Module map

| File | Responsibility |
| --- | --- |
| `debate_timer/app.py` | Assemble the application, initialize state, manage window lifecycle |
| `debate_timer/models.py` | Phase and phase-settings data structures |
| `debate_timer/templates.py` | Template data, validation, repeat expansion, and block editing operations |
| `debate_timer/template_controller.py` | Apply a validated template to the timer |
| `debate_timer/phases.py` | Build the ordered debate schedule, independent of Tkinter |
| `debate_timer/timing.py` | Countdown, pause/resume, navigation, and time adjustment |
| `debate_timer/rebuttal.py` | Robo eligibility, its separate countdown, and time deduction |
| `debate_timer/formatting.py` | Format milliseconds for the clock displays |
| `debate_timer/configuration.py` | Apply settings and connect JSON dialogs to the application |
| `debate_timer/storage.py` | Read and write JSON without UI dependencies |
| `debate_timer/shortcuts.py` | Keyboard shortcuts and input-focus guards |
| `debate_timer/ui/operator.py` | Operator panel and its layout |
| `debate_timer/ui/projector.py` | Audience display, resizing, fullscreen, and blanking |
| `debate_timer/ui/presenter.py` | Render current timer state in both windows |
| `debate_timer/ui/settings.py` | Settings form and Tk variables |
| `debate_timer/ui/styles.py` | Shared colors, typography, and widget helpers |
| `debate_timer/ui/logos.py` | Optional logo loading and rendering |
| `debate_timer/ui/size_editor.py` | Live sizing of projector elements only |
| `debate_timer/ui/block_editor.py` | Visual block palette, drag ordering, properties, teams, and template files |

`app.py` combines focused mixins that operate on the application's shared state.
Only the application owns Tk windows and schedules countdown callbacks. The pure
domain modules (`models`, `phases`, `formatting`, `storage`) can be used and tested
without a desktop. UI component methods retain their original widget creation order
so existing projector-size configuration keys continue to work.

The root `temporizador_debate_v13.py` and `size_editor.py` files are small compatibility
wrappers, not duplicate implementations.

## Test

All checks, including Tkinter integration (requires a desktop):

```console
python -B -m unittest discover -s tests -v
```

Domain-only checks (no desktop required):

```console
python -B -m unittest discover -s tests -p test_domain.py -v
```

The integration suite checks manual robo deduction, clock accuracy, configuration
round-tripping, projector-only size controls, and simulated slider mouse dragging.

## Build the Windows executable

On Windows with Python 3.14 and Tkinter:

```powershell
python -m pip install -r requirements-build.txt
.\Build-Windows.ps1
```

The script builds a standalone `dist/Turno.exe`, runs a bundled-application smoke
check, and creates `dist/Turno-v0.2.0-Windows-x64.zip` with SHA-256 checksums.
The smoke check exercises the frozen executable, its logo renderer and size editor,
and its timer/robo controls. A successful local check does not replace testing on
other Windows machines.

`Turno.spec` controls bundling, `tools/` contains icon/package generation, and
`packaging/` contains Windows metadata and runtime license notices.

## Sharing this project

The source package excludes local logos, school documents, configuration exports,
generated backups, and retired phone/build files. Users select their own logos.

Licensed under the [MIT License](LICENSE).

The application operates offline; it does not publish or upload debate data.
