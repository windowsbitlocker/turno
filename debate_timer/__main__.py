"""Run with python -m debate_timer or the installed debate-timer launcher."""


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Turno - temporizador de debates")
    parser.add_argument("--edit-template", action="store_true", help="Abrir el editor visual de formatos")
    parser.add_argument("--self-test-report", metavar="PATH", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.self_test_report:
        from .diagnostics import smoke_test
        smoke_test(args.self_test_report)
        return
    from .app import TemporizadorDebate
    app = TemporizadorDebate()
    if args.edit_template:
        app.open_template_editor()
    app.run()


if __name__ == "__main__":
    main()
