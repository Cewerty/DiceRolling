import random
from abc import abstractmethod
from typing import Protocol

from dice import Dice


class RandomStrategy(Protocol):
    def randint(self, smallest: int, biggest: int) -> int: ...


class PseudorandomRandomStrategy:
    def randint(self, smallest: int, biggest: int) -> int:
        return random.randint(smallest, biggest)


class MathRandomStrategy:
    def randint(self, smallest: int, biggest: int) -> int:
        import numpy as np  # noqa: PLC0415

        rng = np.random.default_rng()
        return rng.integers(smallest, biggest + 1)


class RollStrategy(Protocol):
    @abstractmethod
    def roll(self, dice: Dice, modifier: int = 0) -> int: ...


class DefaultRoll(RollStrategy):
    def roll(self, dice: Dice, modifier=0):
        return (dice._rng.randint(dice._smallest_side, dice._biggest_side)) + modifier


class DisadvantageRoll(RollStrategy):
    def roll(self, dice: Dice, modifier=0):
        return min(dice._rng.randint(dice._smallest_side, dice._biggest_side) for _ in range(2)) + modifier


class AdvantageRoll(RollStrategy):
    def roll(self, dice: Dice, modifier=0):
        return max(dice._rng.randint(dice._smallest_side, dice._biggest_side) for _ in range(2)) + modifier


class MultipleRoll(RollStrategy):
    def __init__(self, times: int = 1):
        self.times = times

    def roll(self, dice: Dice, modifier=0):
        return sum(dice._rng.randint(dice._smallest_side, dice._biggest_side) for _ in range(self.times)) + modifier
