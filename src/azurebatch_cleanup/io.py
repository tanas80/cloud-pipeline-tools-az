from __future__ import annotations

from typing import Iterable, Protocol


class Printer(Protocol):
    def __call__(self, message: str) -> None: ...


class InputReader(Protocol):
    def __call__(self, prompt: str) -> str: ...


def _default_printer(message: str) -> None:
    print(message)


def _default_reader(prompt: str) -> str:
    return input(prompt)


class ConsoleIO:
    def __init__(self, printer: Printer = _default_printer, reader: InputReader = _default_reader) -> None:
        self.print: Printer = printer
        self.input: InputReader = reader

    def confirm(self, prompt: str) -> bool:
        value = self.input(prompt).strip().lower()
        return value in {"y", "yes"}

    def print_lines(self, lines: Iterable[str]) -> None:
        for line in lines:
            self.print(line)
