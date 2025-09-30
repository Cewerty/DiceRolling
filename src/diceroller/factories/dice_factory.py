"""
Module providing a factory for creating standard RPG dice.

This module contains the DiceFactory class which creates predefined dice types
commonly used in tabletop role-playing games (RPGs). The factory supports creating
individual dice or complete sets with consistent randomization strategies.

Classes:
    DiceFactory: Factory class for creating RPG dice

Example:
-------
    >>> from dice_factory import DiceFactory
    >>> from diceStrategies import DefaultRandomStrategy
    >>> factory = DiceFactory(DefaultRandomStrategy())
    >>> d20 = factory.d20()
    >>> result = d20.roll()
    >>> 1 <= result <= 20
    True

"""

from typing import ClassVar

from ..dice import Dice
from ..strategies import DefaultRandomStrategy, RandomStrategy


class DiceFactory:
    """
    Factory class for creating standard RPG dice.

    Provide methods to create common dice types (d4, d6, d8, etc.)
    using a consistent randomization strategy. All dice created by
    the same factory will share the same random number generation logic.

    Attributes
    ----------
        _random_strategy (RandomStrategy): Randomization strategy for dice rolls
        _TABLES (ClassVar[dict]): Mapping of dice names to their side configurations

    """

    __slots__ = ("_random_strategy",)

    _random_strategy: RandomStrategy

    _TABLES: ClassVar[dict[str, list[int]]] = {
        "d4": [1, 4],
        "d6": [1, 6],
        "d8": [1, 8],
        "d10": [1, 10],
        "d12": [1, 12],
        "d20": [1, 20],
    }

    def __init__(self, random_strategy: RandomStrategy | type[RandomStrategy] | None = None) -> None:
        """
        Initialize the dice factory with a randomization strategy.

        Args:
        ----
            random_strategy: Random number generation strategy for all dice

        Example:
        -------
            >>> from diceStrategies import DefaultRandomStrategy
            >>> factory = DiceFactory(DefaultRandomStrategy())

        """
        if random_strategy is None:
            self._random_strategy = DefaultRandomStrategy()
        elif isinstance(random_strategy, type):
            self._random_strategy = random_strategy()
        else:
            self._random_strategy = random_strategy

    def _make_dice_set(self) -> dict[str, Dice]:
        """
        Create a complete set of standard RPG dice.

        Returns:
        -------
            Dictionary mapping dice names to Dice instances

        Example:
        -------
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
        ----
            smallest_side: Smallest face value of the die
            biggest_side: Largest face value of the die

        Returns:
        -------
            Configured Dice instance

        Note:
        ----
            Uses the factory's randomization strategy

        """
        return Dice(smallest_side, biggest_side, self._random_strategy)
