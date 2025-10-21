"""
Dice simulation module.

This module provides core functionality for dice-based probability simulations.

Provides:
    Dice: Class representing a physical die with configurable strategies

Example:
-------
    Creating and rolling a standard D20::

        >>> from dice import Dice
        >>> d20 = Dice(1, 20)
        >>> roll = d20.roll()
        >>> 1 <= roll <= 20
        True

    Checking success against difficulty::

        >>> d20.check_success(15)  # doctest: +SKIP
        False

Note:
----
    Actual roll results are random. For reproducible documentation examples:
    - Use fixed seed in tests
    - Or mark with ``# doctest: +SKIP``

Warning:
-------
    Creating dice with invalid sides (negative or min > max) raises ValueError

Attributes:
----------
    __version__: Module version string
    DEFAULT_SIDES: Default dice configuration (constant)

Todo:
----
    * Add serialization support
    * Implement dice pool functionality

"""

from __future__ import annotations

import functools
import operator
from collections.abc import Generator, Iterable
from copy import deepcopy
from dataclasses import dataclass, field, replace
from typing import Final

from .strategies import (
    DefaultRandomStrategy,
    DefaultRoll,
    RandomStrategy,
    RollStrategy,
)


@dataclass(slots=True, frozen=True)
class Dice:
    """
    Class for immutable dice.

    Attributes
    ----------
        _smallest_side (int): Smallest side of the die
        _biggest_side (int): Largest side of the die
        _randomization_strategy (RandomStrategy): Random number generation strategy
        _roll_strategy (RollStrategy): Dice rolling strategy

    Raises
    ------
        ValueError: If smallest side is larger than biggest side or negative

    """

    _smallest_side: int
    _biggest_side: int
    _randomization_strategy: Final[RandomStrategy] = field(default_factory=DefaultRandomStrategy)
    _roll_strategy: Final[RollStrategy] = field(default_factory=DefaultRoll)

    def __post_init__(self) -> None:
        """
        Initialize dice side validation.

        Raises
        ------
            ValueError: When smallest side is larger than biggest side or negative

        """
        if self.smallest_side >= self.biggest_side or self.smallest_side < 0:
            raise ValueError(
                f"Incorrect sides: smallest_side ({self._smallest_side}) must be non-negative "
                f"and less than biggest_side ({self._biggest_side})."
            )

    @property
    def smallest_side(self) -> int:
        """
        Get the smallest side of the die.

        Returns:
        -------
            int: Smallest side value (read-only)

        Note:
        ----
            Value is set during instance creation

        """
        return self._smallest_side

    @property
    def biggest_side(self) -> int:
        """
        Get the largest side of the die.

        Returns:
        -------
            int: Largest side value (read-only)

        Note:
        ----
            Value is set during instance creation

        """
        return self._biggest_side

    @property
    def randomization_strategy(self) -> RandomStrategy:
        """
        Get the random number generation strategy.

        Returns:
        -------
            RandomStrategy: Randomization strategy instance

        Note:
        ----
            Value is set during instance creation

        """
        return self._randomization_strategy

    @property
    def roll_strategy(self) -> RollStrategy:
        """
        Get the dice rolling strategy.

        Returns:
        -------
            RollStrategy: Roll strategy instance

        Note:
        ----
            Value is set during instance creation

        """
        return self._roll_strategy

    def check_success(self, check: int, inserted_roll_strategy: RollStrategy | None = None) -> bool:
        """
        Check success against a target number.

        Args:
        ----
            check: Target number to beat
            inserted_roll_strategy: Optional roll strategy override

        Returns:
        -------
            bool: True if roll meets/exceeds target, False otherwise

        """
        return self.roll(inserted_roll_strategy=inserted_roll_strategy) >= check

    def roll(
        self,
        modifier: int = 0,
        inserted_roll_strategy: RollStrategy | None = None,
    ) -> int:
        """
        Roll the die with optional modifier.

        Args:
        ----
            modifier: Roll modifier to add
            inserted_roll_strategy: Optional roll strategy override

        Returns:
        -------
            int: Final roll result

        """
        if inserted_roll_strategy is None:
            return self.roll_strategy.roll(self, modifier)
        return inserted_roll_strategy.roll(self, modifier)

    def __add__(self, other: int) -> int:
        """
        Add an integer modifier or another die to this die.

        When adding an integer, it acts as a modifier to a single roll.
        When adding another die, returns the sum of rolling both dice once.

        Args:
        ----
            other: Integer modifier or another Dice instance

        Returns:
        -------
            int: Result of the roll with modifier or sum of two dice

        Raises:
        ------
            TypeError: If other is neither int nor Dice

        Example:
        -------
            >>> d6 = Dice(1, 6)
            >>> d6 + 2  # Roll d6 with +2 modifier
            5
            >>> d6 + Dice(1, 6)  # Sum of two d6 rolls
            8

        """
        if isinstance(other, int):
            return self.roll(modifier=other)
        elif isinstance(other, Dice):
            return sum([self.roll(), other.roll()])
        else:
            raise TypeError(f"Cannot summarize Dice with {type(other)}")

    def __radd__(self, other: int | Dice) -> int:
        """
        Handle right-side addition for integer modifiers.

        Enables commutative addition with integers (2 + dice).

        Args:
        ----
            other: Integer modifier

        Returns:
        -------
            int: Result of the roll with modifier

        Raises:
        ------
            TypeError: If other is not an integer

        Example:
        -------
            >>> d6 = Dice(1, 6)
            >>> 2 + d6  # Equivalent to d6 + 2
            5

        """
        if isinstance(other, int):
            return self.roll(modifier=other)
        elif isinstance(other, Dice):
            return sum([self.roll(), other.roll()])
        else:
            raise TypeError(f"Cannot summarize Dice with {type(other)}")

    def __sub__(self, other: int | Dice) -> int:
        """
        Subtract an integer or another dice roll from this dice's roll result.

        This method allows subtraction of either an integer (as a modifier) from the
        result of rolling this dice, or the roll result of another dice object from
        this dice's roll result.

        Args:
        ----
            self: The Dice object being rolled.
            other: Either an integer to subtract from the roll result or another Dice
                object whose roll result will be subtracted.

        Returns:
        -------
            The result of subtracting either the integer or the other dice's roll
            from this dice's roll.

        Raises:
        ------
            TypeError: If the operand is neither an integer nor a Dice object.

        Examples:
        --------
            >>> from diceroller.aliases import d6, d20
            >>> d6_obj = d6()
            >>> d6_obj - 2  # Subtract 2 from a d6 roll
            3
            >>> d6_obj - d6()  # Subtract one d6 roll from another
            -1
            >>> d20_obj = d20()
            >>> d20_obj - d6()  # Subtract a d6 roll from a d20 roll
            12

        """
        if isinstance(other, int):
            return self.roll(modifier=-other)
        elif isinstance(other, Dice):
            return functools.reduce(operator.sub, [self.roll(), other.roll()])
        else:
            raise TypeError(f"Cannot subtract Dice with {type(other)}")

    def __rsub__(self, other: int | Dice) -> int:
        """
        Subtract an integer or another dice roll from this dice's roll result.

        This method allows subtraction where this dice object is the right operand,
        such as an integer minus this dice's roll or another dice's roll minus this
        dice's roll.

        Args:
        ----
            self: The Dice object being rolled.
            other: Either an integer from which this dice's roll result is subtracted,
                or another Dice object whose roll result is used as the minuend.

        Returns:
        -------
            The result of subtracting this dice's roll from either the integer or the
            other dice's roll.

        Raises:
        ------
            TypeError: If the operand is neither an integer nor a Dice object.

        Examples:
        --------
            >>> from diceroller.aliases import d6, d20
            >>> d6_obj = d6()
            >>> 5 - d6_obj  # Subtract a d6 roll from 5
            2
            >>> d20_obj = d20()
            >>> d20_obj - d6_obj  # Subtract a d6 roll from a d20 roll
            12
            >>> d6_obj2 = d6()
            >>> d6_obj2 - d6_obj  # Subtract one d6 roll from another
            -1

        """
        if isinstance(other, int):
            return other - self.roll()
        elif isinstance(other, Dice):
            return other.roll() - self.roll()
        else:
            raise TypeError(f"Cannot subtract Dice with {type(other)}")

    def __deepcopy__(self, memo: dict[int, object]) -> Dice:
        """
        Create a deep copy of this Dice instance.

        Handles copying of randomization and roll strategies while
        preserving the frozen and slotted nature of the class.

        Args:
        ----
            memo: Dictionary used by deepcopy to avoid infinite recursion

        Returns:
        -------
            Dice: New Dice instance with copied strategies

        Note:
        ----
            If strategy copying fails, returns the original instance

        """
        try:
            new_random_strategy = deepcopy(self._randomization_strategy, memo)
            new_roll_strategy = deepcopy(self._roll_strategy, memo)
            return replace(self, _randomization_strategy=new_random_strategy, _roll_strategy=new_roll_strategy)
        except Exception:
            return self

    def __mul__(self, other: int | Dice) -> int:
        """
        Multiply the die by an integer to create multiple copies.

        Args:
        ----
            other: Integer multiplier specifying how many copies to create

        Returns:
        -------
            list[Dice]: List of deepcopied Dice instances

        Example:
        -------
            >>> d6 = Dice(1, 6)
            >>> 3 * d6  # Creates three identical d6 dice
            [Dice(1,6), Dice(1,6), Dice(1,6)]

        """
        if isinstance(other, int):
            return sum([self.roll() for _ in range(other)])
        else:
            raise TypeError(f"Cannot multiply Dice with {type(other)}")

    def __rmul__(self, other: int | Dice) -> list[Dice]:
        """
        Handle right-side multiplication for integer multipliers.

        Enables commutative multiplication with integers (3 * dice).

        Args:
        ----
            other: Integer multiplier specifying how many copies to create

        Returns:
        -------
            list[Dice]: List of deepcopied Dice instances

        Example:
        -------
            >>> d6 = Dice(1, 6)
            >>> 3 * d6  # Creates three identical d6 dice
            [Dice(1,6), Dice(1,6), Dice(1,6)]

        """
        if isinstance(other, int):
            return [deepcopy(self) for _ in range(other)]
        else:
            raise TypeError(f"Cannot multiply Dice with {type(other)}")


def adv(dices: Dice | Iterable[Dice]) -> int:
    """
    Return the maximum roll result from a collection of dice.

    This function accepts either a single dice object or a collection of dice objects,
    rolls all dice, and returns the highest result obtained.

    Args:
    ----
        dices: An object implementing the Dice interface, or an iterable collection
               of such objects.

    Returns:
    -------
        The highest value among all dice roll results.

    Raises:
    ------
        TypeError: If the provided argument is not a dice object or iterable collection,
                   or if any element in the collection doesn't implement the Dice interface.

    Examples:
    --------
        >>> from diceroller.aliases import d6, d20
        >>> adv(d6())  # Single dice
        4
        >>> adv([d6(), d6(), d6()])  # Multiple dice
        6
        >>> adv([d6(), d20()])  # Mixed dice types
        18

    """
    if isinstance(dices, Dice):
        return max(dices.roll(), dices.roll())
    elif not isinstance(dices, Iterable):
        raise TypeError("Item does not implement the Dice interface.")
    for i, item in enumerate(dices):
        if not isinstance(item, Dice):
            raise TypeError(f"Item with index {i} does not implement the Dice interface.")
    return max(die.roll() for _, die in enumerate(dices))


def dis(dices: Dice | Iterable[Dice]) -> int:
    """
    Return the minimum roll result from a collection of dice.

    This function accepts either a single dice object or a collection of dice objects,
    rolls all dice, and returns the lowest result obtained.

    Args:
    ----
        dices: An object implementing the Dice interface, or an iterable collection
               of such objects.

    Returns:
    -------
        The lowest value among all dice roll results.

    Raises:
    ------
        TypeError: If the provided argument is not a dice object or iterable collection,
                   or if any element in the collection doesn't implement the Dice interface.

    Examples:
    --------
        >>> from diceroller.aliases import d6, d20
        >>> dis(d6())  # Single dice
        2
        >>> dis([d6(), d6(), d6()])  # Multiple dice
        1
        >>> dis([d6(), d20()])  # Mixed dice types
        3

    """
    if isinstance(dices, Dice):
        return min(dices.roll(), dices.roll())
    elif not isinstance(dices, Iterable):
        raise TypeError("Item does not implement the Dice interface.")
    for i, item in enumerate(dices):
        if not isinstance(item, Dice):
            raise TypeError(f"Item with index {i} does not implement the Dice interface.")
    return min(die.roll() for _, die in enumerate(dices))


def throws(dice: Dice, count: int = 1, roll_modificator: int = 0) -> Generator[int, None, None]:
    """
    Generate a sequence of dice roll results for a specified number of throws.

    This function takes a single dice object, rolls it the specified number of times,
    and yields each roll result with an optional modifier applied.

    Args:
    ----
        dice: An object implementing the Dice interface, with a roll method.
        count: The number of times to roll the dice (default: 1).
        roll_modificator: An integer to add to each roll result (default: 0).

    Yields:
    ------
        The result of each dice roll, with the modifier applied.

    Raises:
    ------
        ValueError: If the count of throws is negative.
        TypeError: If the provided dice argument does not implement the Dice interface.

    Examples:
    --------
        >>> from diceroller.aliases import d6, d20
        >>> list(throws(d6()))  # Single roll of a d6
        [4]
        >>> list(throws(d6(), count=3))  # Three rolls of a d6
        [2, 5, 1]
        >>> list(throws(d20(), count=2, roll_modificator=3))  # Two rolls of a d20 with +3 modifier
        [15, 8]

    """
    if not isinstance(dice, Dice):
        raise TypeError("Provided argument does not implement the Dice interface.")
    if count < 0:
        raise ValueError("Cannot roll a die a negative number of times.")
    while count > 0:
        yield dice.roll(modifier=roll_modificator)
        count -= 1
