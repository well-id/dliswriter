from collections.abc import Sequence
from typing import Generator


class SizedGenerator(Sequence):
    def __init__(self, generator: Generator, size: int) -> None:
        self._generator = generator
        self._size = size

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Generator:
        yield from self._generator

    def __getitem__(self, index: int) -> None:
        raise NotImplementedError("SizedGenerator does not support item access")
