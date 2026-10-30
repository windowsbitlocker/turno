"""Packaged-application smoke check; run explicitly via --self-test-report PATH."""
import json
from pathlib import Path
import sys


def smoke_test(report_path: str) -> None:
    from PIL import Image
    from tkinter import font as tkfont
    from .app import TemporizadorDebate
    from .ui.logos import PIL_AVAILABLE
    report = Path(report_path).resolve()
    report.parent.mkdir(parents=True, exist_ok=True)
    app = None
    result = {"ok": False, "frozen": bool(getattr(sys, "frozen", False))}
    try:
        app = TemporizadorDebate()
        app.root.withdraw()
        app.display.withdraw()
        app.root.update()
        assert len(app.phases) == 20
        assert PIL_AVAILABLE
        app.start_pause_button.invoke()
        assert app.running
        app.pause()
        app.load_phase(17)
        app.start_steal()
        assert app.robo_active
        app.robo_remaining_ms -= 1000
        before = app.remaining_ms
        app.end_steal_now()
        assert not app.robo_active and app.remaining_ms <= before - 1000
        app.size_editor.open(app.display_timer_label)
        app.size_editor.set_value(app.display_timer_label, "font_size", 80)
        assert tkfont.Font(font=app.display_timer_label["font"]).actual("size") == 80
        logo = report.parent / "smoke-logo.png"
        Image.new("RGB", (100, 60), "white").save(logo)
        app.logo_paths = [str(logo)]
        app.load_logos()
        assert len(app.logo_imgs) == 1
        app.root.update()
        result.update(ok=True, phases=20, logos=True, projector_editor=True, robo=True)
    except Exception as error:
        result["error"] = str(error)
        raise
    finally:
        if app is not None:
            app.close_app()
        report.write_text(json.dumps(result, indent=2), encoding="utf-8")
