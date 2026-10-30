"""Compatibility entry point; implementation lives in the debate_timer package."""
from debate_timer.app import TemporizadorDebate
from debate_timer.models import Phase
from debate_timer.__main__ import main

__all__ = ["TemporizadorDebate", "Phase"]

if __name__ == "__main__":
    main()
