"""Run with python -m debate_timer or the installed debate-timer launcher."""


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Turno - temporizador de debates")
    parser.add_argument("--self-test-report", metavar="PATH", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.self_test_report:
        from .diagnostics import smoke_test
        smoke_test(args.self_test_report)
        return
    from .app import TemporizadorDebate
    TemporizadorDebate().run()


if __name__ == "__main__":
    main()
