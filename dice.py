from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Protocol

from diceStrategies import (
    DefaultRandomStrategy,
    DefaultRoll,
    MathRandomStrategy,
    PseudorandomRandomStrategy,
    RandomStrategy,
    RollStrategy,
)


@dataclass(slots=True)
class Dice(ABC):
    _smallest_side: int
    _biggest_side: int
    _randomizationStrategy: RandomStrategy = field(default_factory=DefaultRandomStrategy)
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
        return self._randomizationStrategy

    @property
    def rollStrategy(self):
        return self._rollStrategy

    @rollStrategy.setter
    def rollStrategy(self, newRollStrategy: RollStrategy):
        self._rollStrategy = newRollStrategy

    def check_success(self, check: int) -> bool:
        return self.roll() >= check

    def roll(self, modifier: int = 0) -> int:
        return self.rollStrategy.roll(self, modifier)


class AbstractDiceFabric(Protocol):
    @abstractmethod
    def get_randomizationStrategy(self): ...

    def create_dice_set(self) -> dict:
        return {
            "d4": self.create_d4(),
            "d6": self.create_d6(),
            "d8": self.create_d8(),
            "d10": self.create_d10(),
            "d12": self.create_d12(),
            "d20": self.create_d20(),
        }

    def create_d4(self):
        return Dice(1, 4, self.get_randomizationStrategy())

    def create_d6(self):
        return Dice(1, 6, self.get_randomizationStrategy())

    def create_d8(self):
        return Dice(1, 8, self.get_randomizationStrategy())

    def create_d10(self):
        return Dice(0, 9, self.get_randomizationStrategy())

    def create_d12(self):
        return Dice(1, 12, self.get_randomizationStrategy())

    def create_d20(self):
        return Dice(1, 20, self.get_randomizationStrategy())


class PseudorandomDiceFabric(AbstractDiceFabric):
    def get_randomizationStrategy(self):
        if not hasattr(self, "_randomizationStrategy"):
            self._randomizationStrategy = PseudorandomRandomStrategy()
        return self._randomizationStrategy


class DefaultDiceFabric(AbstractDiceFabric):
    def get_randomizationStrategy(self):
        if not hasattr(self, "_randomizationStrategy"):
            self._randomizationStrategy = DefaultRandomStrategy()
        return self._randomizationStrategy


class MathematicalDiceFabric(AbstractDiceFabric):
    def get_randomizationStrategy(self):
        if not hasattr(self, "_randomizationStrategy"):
            self._randomizationStrategy = MathRandomStrategy()
        return self._randomizationStrategy
