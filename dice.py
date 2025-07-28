from abc import ABC
from dataclasses import dataclass, field
from random import SystemRandom

from diceStrategies import DefaultRoll, RandomStrategy, RollStrategy


@dataclass(slots=True)
class Dice(ABC):
    _smallest_side: int
    _biggest_side: int
    _randomizationStrategy: RandomStrategy = field(default_factory=SystemRandom)
    _rollStrategy: RollStrategy = field(default_factory=DefaultRoll)

    def __post_init__(self):
        if not (
            (self._smallest_side >= 0)
            and ((self._smallest_side != self._biggest_side) or (self._smallest_side > self._biggest_side))
        ):
            return ValueError("Not correct sides value!")

    @property
    def smallest_side(self):
        return self._smallest_side

    @property
    def biggest_side(self):
        return self._biggest_side

    @property
    def randomizationStrategy(self) -> RandomStrategy:
        return self._rng

    @randomizationStrategy.setter
    def randomizationStrategy(self, newStrategy: RandomStrategy) -> None:
        self._rng = newStrategy

    @property
    def rollStrategy(self):
        return self._rollStrategy

    @rollStrategy.setter
    def rollStrategy(self, newRollStrategy: RollStrategy):
        self._rollStrategy = newRollStrategy

    def check_success(self, check: int) -> bool:
        return self.roll() >= check

    def roll(self, modifier: int = 0) -> int:
        return self._rollStrategy.roll(self, modifier)
