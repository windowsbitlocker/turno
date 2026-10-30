"""Run with python -m debate_timer or the installed debate-timer launcher."""


def main():
    from .app import TemporizadorDebate
    TemporizadorDebate().run()


if __name__ == "__main__":
    main()
