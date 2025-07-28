from __future__ import annotations

import random
from abc import abstractmethod
from secrets import SystemRandom
from typing import Protocol


class RandomStrategy(Protocol):
    def randint(self, smallest: int, biggest: int) -> int: ...


class DefaultRandomStrategy:
    def randint(self, smallest: int, biggest: int) -> int:
        return SystemRandom().randint(smallest, biggest)


class PseudorandomRandomStrategy:
    def randint(self, smallest: int, biggest: int) -> int:
        return random.randint(smallest, biggest)


class MathRandomStrategy:
    def randint(self, smallest: int, biggest: int) -> int:
        import numpy as np  # noqa: PLC0415

        rng = np.random.default_randomizationStrategy()
        return rng.integers(smallest, biggest + 1)


class RollStrategy(Protocol):
    @abstractmethod
    def roll(self, dice: Dice, modifier: int = 0) -> int: ...  # noqa: F821


class DefaultRoll(RollStrategy):
    def roll(self, dice: Dice, modifier=0):  # noqa: F821
        return (dice.randomizationStrategy.randint(dice.smallest_side, dice.biggest_side)) + modifier


class DisadvantageRoll(RollStrategy):
    def roll(self, dice: Dice, modifier=0):  # noqa: F821
        return (
            min(dice.randomizationStrategy.randint(dice._smallest_side, dice._biggest_side) for _ in range(2))
            + modifier
        )


class AdvantageRoll(RollStrategy):
    def roll(self, dice: Dice, modifier=0):  # noqa: F821
        return (
            max(dice.randomizationStrategy.randint(dice._smallest_side, dice._biggest_side) for _ in range(2))
            + modifier
        )


class MultipleRoll(RollStrategy):
    def __init__(self, times: int = 1):
        self.times = times

    def roll(self, dice: Dice, modifier=0):  # noqa: F821
        return (
            sum(dice.randomizationStrategy.randint(dice._smallest_side, dice._biggest_side) for _ in range(self.times))
            + modifier
        )
