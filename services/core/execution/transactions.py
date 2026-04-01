from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from threading import RLock
from typing import Callable, Iterator


@dataclass
class TransactionContext:
    rollback_actions: list[Callable[[], None]] = field(default_factory=list)
    committed: bool = False


class TransactionManager:
    """Simple atomic transaction + compensation coordinator."""

    def __init__(self) -> None:
        self._lock = RLock()

    @contextmanager
    def unit_of_work(self) -> Iterator[TransactionContext]:
        ctx = TransactionContext()
        with self._lock:
            try:
                yield ctx
                ctx.committed = True
            except Exception:
                for action in reversed(ctx.rollback_actions):
                    action()
                raise

    @staticmethod
    def add_compensation(ctx: TransactionContext, action: Callable[[], None]) -> None:
        ctx.rollback_actions.append(action)
