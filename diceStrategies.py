"""
_summary_.

Returns:
    _type_: _description_
        
"""
from __future__ import annotations

import random
from collections.abc import Generator
from secrets import SystemRandom
from typing import TYPE_CHECKING, ClassVar, Protocol

import numpy as np

if TYPE_CHECKING:
    from dice import Dice


class RandomStrategy(Protocol):
    def randint(self, smallest: int, biggest: int) -> int: ...


class DefaultRandomStrategy:
    def __init__(self) -> None:
        self._systemRandom: SystemRandom = SystemRandom()

    def randint(self, smallest: int, biggest: int) -> int:
        return self._systemRandom.randint(a=smallest, b=biggest)


class PseudoRandomStrategy:
    def randint(self, smallest: int, biggest: int) -> int:
        return random.randint(smallest, biggest)


class NumPyStrategy:
    def __init__(self) -> None:
        self._rng: Generator = np.random.default_rng()

    def randint(self, smallest: int, biggest: int) -> int:
        return int(self._rng.integers(smallest, biggest + 1))


class RollStrategy(Protocol):
    def roll(self, dice: Dice, modifier: int = 0) -> int: ...


class DefaultRoll:
    def roll(self, dice: Dice, modifier: int = 0) -> int:
        return (dice.randomizationStrategy.randint(dice.smallest_side, dice.biggest_side)) + modifier


class DisadvantageRoll:
    def roll(self, dice: Dice, modifier: int = 0) -> int:
        first_roll = dice.randomizationStrategy.randint(dice.smallest_side, dice.biggest_side)
        second_roll = dice.randomizationStrategy.randint(dice.smallest_side, dice.biggest_side)
        return min(first_roll, second_roll) + modifier


class AdvantageRoll:
    def roll(self, dice: Dice, modifier: int = 0) -> int:
        first_roll = dice.randomizationStrategy.randint(dice.smallest_side, dice.biggest_side)
        second_roll = dice.randomizationStrategy.randint(dice.smallest_side, dice.biggest_side)
        return max(first_roll, second_roll) + modifier


class MultipleRoll:
    __slots__: tuple = ("_times",)

    _instances: ClassVar[dict[int, MultipleRoll]] = {}

    def __new__(cls, times: int = 1) -> MultipleRoll:
        if times not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[times] = instance
        return cls._instances[times]

    def __init__(self, times: int = 1) -> MultipleRoll | None:
        if not hasattr(self, "_times"):
            self._times = times

    @property
    def times(self) -> int:
        return self._times

    def roll(self, dice: Dice, modifier: int = 0) -> int:
        return (
            sum(dice.randomizationStrategy.randint(dice.smallest_side, dice.biggest_side) for _ in range(self.times))
            + modifier
        )
