"""
Module providing a factory for creating standard RPG dice.

This module contains the DiceFactory class which creates predefined dice types
commonly used in tabletop role-playing games (RPGs). The factory supports creating
individual dice or complete sets with consistent randomization strategies.

Classes:
    DiceFactory: Factory class for creating RPG dice

Example:
    >>> from dice_factory import DiceFactory
    >>> from diceStrategies import DefaultRandomStrategy
    >>> factory = DiceFactory(DefaultRandomStrategy())
    >>> d20 = factory.d20()
    >>> result = d20.roll()
    >>> 1 <= result <= 20
    True

"""

from typing import ClassVar

from .dice import Dice
from .dice_strategies import RandomStrategy


class DiceFactory:
    """
    Factory class for creating standard RPG dice.

    Provide methods to create common dice types (d4, d6, d8, etc.)
    using a consistent randomization strategy. All dice created by
    the same factory will share the same random number generation logic.

    Attributes:
        _randomStrategy (RandomStrategy): Randomization strategy for dice rolls
        _TABLES (ClassVar[dict]): Mapping of dice names to their side configurations

    """

    __slots__ = ("_randomStrategy",)

    _TABLES: ClassVar[dict[str, [int, int]]] = {
        "d4": [1, 4],
        "d6": [1, 6],
        "d8": [1, 8],
        "d10": [0, 9],
        "d12": [1, 12],
        "d20": [1, 20],
    }

    def __init__(self, random_strategy: RandomStrategy) -> None:
        """
        Initialize the dice factory with a randomization strategy.

        Args:
            random_strategy: Random number generation strategy for all dice

        Example:
            >>> from diceStrategies import DefaultRandomStrategy
            >>> factory = DiceFactory(DefaultRandomStrategy())

        """
        self._randomStrategy: RandomStrategy = random_strategy

    def _make_dice_set(self) -> dict[str, Dice]:
        """
        Create a complete set of standard RPG dice.

        Returns:
            Dictionary mapping dice names to Dice instances

        Example:
            >>> factory = DiceFactory(DefaultRandomStrategy())
            >>> dice_set = factory._make_dice_set()
            >>> "d20" in dice_set
            True

        """
        return {
            name: self._make_dice(smallest_side=sides[0], biggest_side=sides[1]) for name, sides in self._TABLES.items()
        }

    def _make_dice(self, smallest_side: int, biggest_side: int) -> Dice:
        """
        Create a single die with specified parameters.

        Args:
            smallest_side: Smallest face value of the die
            biggest_side: Largest face value of the die

        Returns:
            Configured Dice instance

        Note:
            Uses the factory's randomization strategy

        """
        return Dice(smallest_side, biggest_side, self._randomStrategy)

    def d4(self) -> Dice:
        """
        Create a standard 4-sided die (d4).

        Returns:
            Dice: 4-sided die (1-4)

        """
        return self._make_dice(1, 4)

    def d6(self) -> Dice:
        """
        Create a standard 6-sided die (d6).

        Returns:
            Dice: 6-sided die (1-6)

        """
        return self._make_dice(1, 6)

    def d8(self) -> Dice:
        """
        Create a standard 8-sided die (d8).

        Returns:
            Dice: 8-sided die (1-8)

        """
        return self._make_dice(1, 8)

    def d10(self) -> Dice:
        """
        Create a standard 10-sided die (d10) with RPG-specific range.

        Returns:
            Dice: 10-sided die (0-9)

        Note:
            Uses 0-9 range for compatibility with percentile dice systems in RPGs

        """
        return self._make_dice(0, 9)

    def d12(self) -> Dice:
        """
        Create a standard 12-sided die (d12).

        Returns:
            Dice: 12-sided die (1-12)

        """
        return self._make_dice(1, 12)

    def d20(self) -> Dice:
        """
        Create a standard 20-sided die (d20).

        Returns:
            Dice: 20-sided die (1-20)

        """
        return self._make_dice(1, 20)
