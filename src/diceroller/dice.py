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
import heapq
import operator
from abc import ABC, abstractmethod
from collections.abc import Generator, Iterable
from copy import deepcopy
from dataclasses import dataclass, field, replace
from typing import Final

from .exceptions import (
    DiceInvalidAmountError,
    DiceInvalidSidesError,
    DiceOperationTypeError,
    InvalidDiceError,
    InvalidDiceInputError,
    NegativeThrowCountError,
)
from .strategies import (
    DefaultRandomStrategy,
    DefaultRoll,
    RandomStrategy,
    RollStrategy,
)


class Diceable(ABC):
    """Interface for dice-like clasess."""

    @abstractmethod
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
        pass

    @abstractmethod
    def roll(
        self,
        modifier: int = 0,
        inserted_roll_strategy: RollStrategy | None = None,
    ) -> int | list[int]:
        """
        Roll the die with optional modifier.

        Args:
        ----
            modifier: Roll modifier to add
            inserted_roll_strategy: Optional roll strategy override

        Returns:
        -------
            int | list[int]: Final roll result

        """
        pass


@dataclass(slots=True, frozen=True)
class Dice(Diceable):
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
        DiceInvalidSidesError: If smallest side is larger than biggest side or negative

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
            DiceInvalidSidesError: When smallest side is larger than biggest side or negative

        """
        if self.smallest_side >= self.biggest_side or self.smallest_side < 0:
            raise DiceInvalidSidesError(
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
            DiceOperationTypeError: If other is neither int nor Dice

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
            raise DiceOperationTypeError(f"Cannot summarize Dice with {type(other)}")

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
            DiceOperationTypeError: If other is not an integer

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
            raise DiceOperationTypeError(f"Cannot summarize Dice with {type(other)}")

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
            DiceOperationTypeError: If the operand is neither an integer nor a Dice object.

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
            raise DiceOperationTypeError(f"Cannot subtract Dice with {type(other)}")

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
            DiceOperationTypeError: If the operand is neither an integer nor a Dice object.

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
            raise DiceOperationTypeError(f"Cannot subtract Dice with {type(other)}")

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
            raise DiceOperationTypeError(f"Cannot multiply Dice with {type(other)}")

    def __rmul__(self, other: int | Diceable) -> list[Dice] | int:
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
        elif isinstance(other, Dice):
            return self.roll() * other.roll()
        elif isinstance(other, DicePool):
            return self.roll() * sum(other.roll())
        else:
            raise DiceOperationTypeError(f"Cannot multiply Dice with {type(other)}")


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
        DiceOperationTypeError: If the provided argument is not a dice object or iterable collection,
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
        raise InvalidDiceInputError("Item does not implement the Dice interface.")
    for i, item in enumerate(dices):
        if not isinstance(item, Dice):
            raise InvalidDiceInputError(f"Item with index {i} does not implement the Dice interface.")
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
        DiceOperationTypeError: If the provided argument is not a dice object or iterable collection,
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
        raise DiceOperationTypeError("Item does not implement the Dice interface.")
    for i, item in enumerate(dices):
        if not isinstance(item, Diceable):
            raise DiceOperationTypeError(f"Item with index {i} does not implement the Diceable interface.")
    return min(die.roll() for _, die in enumerate(dices))


def _to_dice_list(dices: Dice | list[Dice]) -> list[Dice]:
    """Help to normalize input to list of Dice."""
    if isinstance(dices, Dice):
        return [dices]
    elif isinstance(dices, DicePool):
        return _to_dice_list(dices._dice_list)
    elif isinstance(dices, list):
        flat = []
        for item in dices:
            flat.extend(_to_dice_list(item))
        return flat
    if not isinstance(dices, list):
        raise InvalidDiceInputError("Input must be a Dice, DicePool or list of Dice.")
    return dices


def kh(dices: Dice | list[Dice], keep: int) -> list[int]:
    """
    Keep the highest 'keep' rolls from the dice.

    Returns sorted list of kept rolls (descending). Efficient for large sets using heap.
    """
    dice_list = _to_dice_list(dices)
    n = len(dice_list)
    if keep <= 0:
        raise DiceInvalidAmountError(f"Cannot keep non-positive number of dice: {keep}")
    if keep > n:
        raise DiceInvalidAmountError(f"Cannot keep more dice than available: {keep} > {n}")
    rolls = [die.roll() for die in dice_list]
    return heapq.nlargest(keep, rolls)


def kl(dices: Dice | list[Dice], keep: int) -> list[int]:
    """
    Keep the lowest 'keep' rolls from the dice.

    Returns sorted list of kept rolls (ascending). Efficient for large sets using heap.
    """
    dice_list = _to_dice_list(dices)
    n = len(dice_list)
    if keep <= 0:
        raise DiceInvalidAmountError(f"Cannot keep non-positive number of dice: {keep}")
    if keep > n:
        raise DiceInvalidAmountError(f"Cannot keep more dice than available: {keep} > {n}")
    rolls = [die.roll() for die in dice_list]
    return heapq.nsmallest(keep, rolls)


def dh(dices: Dice | list[Dice], drop: int) -> list[int]:
    """
    Drop the highest 'drop' rolls from the dice (equivalent to keep lowest n-drop).

    Returns sorted list of remaining rolls (ascending). Handles drop=0 (all rolls) and drop=n (empty).
    """
    dice_list = _to_dice_list(dices)
    n = len(dice_list)
    if drop < 0:
        raise DiceInvalidAmountError(f"Cannot drop negative number of dice: {drop}")
    if drop > n:
        raise DiceInvalidAmountError(f"Cannot drop more dice than available: {drop} > {n}")
    if drop == 0:
        rolls = [die.roll() for die in dice_list]
        return sorted(rolls)
    keep = n - drop
    rolls = [die.roll() for die in dice_list]
    return heapq.nsmallest(keep, rolls)


def dl(dices: Dice | list[Dice], drop: int) -> list[int]:
    """
    Drop the lowest 'drop' rolls from the dice (equivalent to keep highest n-drop).

    Returns sorted list of remaining rolls (descending). Handles drop=0 (all rolls) and drop=n (empty).
    """
    dice_list = _to_dice_list(dices)
    n = len(dice_list)
    if drop < 0:
        raise DiceInvalidAmountError(f"Cannot drop negative number of dice: {drop}")
    if drop > n:
        raise DiceInvalidAmountError(f"Cannot drop more dice than available: {drop} > {n}")
    if drop == 0:
        rolls = [die.roll() for die in dice_list]
        return sorted(rolls, reverse=True)
    keep = n - drop
    rolls = [die.roll() for die in dice_list]
    return heapq.nlargest(keep, rolls)


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
        NegativeThrowCountError: If the count of throws is negative.
        InvalidDiceError: If the provided dice argument does not implement the Dice interface.

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
        raise InvalidDiceError("Provided argument does not implement the Dice interface.")
    if count < 0:
        raise NegativeThrowCountError("Cannot roll a die a negative number of times.")
    while count > 0:
        yield dice.roll(modifier=roll_modificator)
        count -= 1


def get_rolls(d: Diceable) -> list[int]:
    """
    Help to normalize Diceable roll result to a list of integers.

    Ensures that roll() output is always a list, even for single Dice.

    Args:
    ----
        d: Diceable instance to roll

    Returns:
    -------
        list[int]: List of roll results

    Example:
    -------
        >>> from diceroller.aliases import d6
        >>> dice = d6()
        >>> get_rolls(dice)
        [4]
        >>> pool = DicePool([d6(), d6()])
        >>> get_rolls(pool)
        [3, 5]

    """
    r = d.roll()
    return r if isinstance(r, list) else [r]


class DicePool(Diceable):
    """
    Class for mutable dice pools.

    Represents a collection of Dice objects, allowing dynamic addition and removal.
    Provides a unified interface similar to Dice for rolling and operations.

    Attributes:
    ----------
        _dice_list (list[Dice]): List of Dice instances in the pool

    Raises:
    ------
        InvalidDiceInputError: If invalid items are added during initialization

    Example:
    -------
        Creating a pool of three d6 dice::

            >>> from diceroller.aliases import d6
            >>> pool = DicePool([d6(), d6(), d6()])
            >>> rolls = pool.roll()
            >>> len(rolls) == 3
            True

    Note:
    ----
        DicePool is mutable, allowing addition/removal of dice after creation.

    """

    __slots__: tuple[str] = ("_dice_list",)

    def __init__(self, dices: list[Dice] | Dice) -> None:
        """
        Initialize the dice pool with given dice.

        Args:
        ----
            dices: Single Dice or list of Dice to include in the pool

        Raises:
        ------
            InvalidDiceInputError: If input contains invalid items

        Example:
        -------
            >>> from diceroller.aliases import d6
            >>> pool = DicePool(d6())  # Single die pool
            >>> len(pool._dice_list) == 1
            True
            >>> pool = DicePool([d6(), d6()])
            >>> len(pool._dice_list) == 2
            True

        """
        self._dice_list = [dice for dice in _to_dice_list(dices)]

    def check_success(self, check: int, inserted_roll_strategy: RollStrategy | None = None) -> bool:
        """
        Check success against a target number for the pool sum.

        Rolls all dice in the pool, sums the results, and checks against the target.

        Args:
        ----
            check: Target number to beat
            inserted_roll_strategy: Optional roll strategy override for all dice

        Returns:
        -------
            bool: True if sum meets/exceeds target, False otherwise

        """
        return sum(self.roll(inserted_roll_strategy=inserted_roll_strategy)) >= check

    def roll(
        self,
        modifier: int = 0,
        inserted_roll_strategy: RollStrategy | None = None,
    ) -> list[int]:
        """
        Roll all dice in the pool with optional modifier.

        Args:
        ----
            modifier: Roll modifier to add to each die
            inserted_roll_strategy: Optional roll strategy override for all dice

        Returns:
        -------
            list[int]: List of individual roll results with modifier

        """
        if inserted_roll_strategy is None:
            return [dice.roll(modifier, inserted_roll_strategy=inserted_roll_strategy) for dice in self._dice_list]
        return [dice.roll(modifier) for dice in self._dice_list]

    def add_dice(self, added_dice: Dice) -> None:
        """
        Add one or more dice to the pool.

        Args:
        ----
            added_dice: Single Dice or list of Dice to add

        Raises:
        ------
            InvalidDiceInputError: If added items are invalid

        Example:
        -------
            >>> from diceroller.aliases import d6
            >>> pool = DicePool(d6())
            >>> pool.add_dice(d6())
            >>> len(pool._dice_list) == 2
            True

        """
        self._dice_list.append(added_dice)

    def remove_dice(self, dice_to_remove: Dice) -> None:
        """
        Remove specified dice from the pool.

        Removes the first occurrence of the matching dice.

        Args:
        ----
            dice_to_remove: Single Diceable or list of Diceable to remove

        Raises:
        ------
            ValueError: If item not found in the pool
            InvalidDiceInputError: If input is invalid

        Example:
        -------
            >>> from diceroller.aliases import d6
            >>> pool = DicePool([d6(), d6()])
            >>> dice = pool._dice_list[0]
            >>> pool.remove_dice(dice)
            >>> len(pool._dice_list) == 1
            True

        """
        self._dice_list.remove(dice_to_remove)

    def remove_dice_by_index(self, index_of_dice: int) -> None:
        """
        Remove dice from the pool by index.

        Args:
        ----
            index_of_dice: Index of the dice to remove (0-based)

        Raises:
        ------
            IndexError: If index is out of range

        Example:
        -------
            >>> from diceroller.aliases import d6
            >>> pool = DicePool([d6(), d6()])
            >>> pool.remove_dice_by_index(0)
            >>> len(pool._dice_list) == 1
            True

        """
        self._dice_list.pop(index_of_dice)

    def __add__(self, other: int | Diceable) -> int | list[int]:
        """
        Add an integer modifier or another Diceable to this pool.

        When adding an integer, it acts as a modifier to the pool sum.
        When adding another Diceable, returns the sum of rolling both.

        Args:
        ----
            other: Integer modifier or another Diceable instance

        Returns:
        -------
            int: Result of the roll with modifier or sum of rolls

        Raises:
        ------
            DiceOperationTypeError: If other is neither int nor Diceable

        Example:
        -------
            >>> from diceroller.aliases import d6
            >>> pool = DicePool([d6(), d6()])
            >>> pool + 2  # Sum of pool rolls with +2 modifier
            7
            >>> pool + d6()  # Sum of pool rolls and another d6 roll
            9

        """
        if isinstance(other, int):
            return self.roll(modifier=other)
        elif isinstance(other, DicePool):
            return sum(get_rolls(self) + get_rolls(other))
        elif isinstance(other, Dice):
            return other.roll() + sum(get_rolls(self))
        else:
            raise DiceOperationTypeError(f"Cannot summarize Dice with {type(other)}")

    def __radd__(self, other: int | Diceable) -> int | list[int]:
        """
        Handle right-side addition for integer modifiers or Diceable.

        Enables commutative addition with integers or Diceable (other + pool).

        Args:
        ----
            other: Integer modifier or Diceable instance

        Returns:
        -------
            int: Result of the roll with modifier or sum of rolls

        Raises:
        ------
            DiceOperationTypeError: If other is neither int nor Diceable

        Example:
        -------
            >>> from diceroller.aliases import d6
            >>> pool = DicePool([d6(), d6()])
            >>> 2 + pool  # Equivalent to pool + 2
            7

        """
        if isinstance(other, int):
            return self.roll(modifier=other)
        elif isinstance(other, Diceable):
            return sum(get_rolls(other) + get_rolls(self))
        else:
            raise DiceOperationTypeError(f"Cannot summarize Dice with {type(other)}")

    def __sub__(self, other: int | Dice) -> int | list[int]:
        """
        Subtract an integer or another Diceable roll from this pool sum.

        Args:
        ----
            other: Integer to subtract or Diceable whose roll sum is subtracted

        Returns:
        -------
            int: Result of subtraction

        Raises:
        ------
            DiceOperationTypeError: If other is neither int nor Diceable

        Example:
        -------
            >>> from diceroller.aliases import d6
            >>> pool = DicePool([d6(), d6()])
            >>> pool - 2  # Pool sum with -2 modifier
            3
            >>> pool - d6()  # Pool sum minus another d6 roll
            2

        """
        if isinstance(other, int):
            return self.roll(modifier=-other)
        elif isinstance(other, DicePool):
            return sum(get_rolls(other)) - sum(get_rolls(self))
        elif isinstance(other, Dice):
            return other.roll() - sum(get_rolls(self))
        else:
            raise DiceOperationTypeError(f"Cannot subtract Dice with {type(other)}")

    def __rsub__(self, other: int | Diceable) -> int:
        """
        Handle right-side subtraction (other - pool sum).

        Args:
        ----
            other: Integer or Diceable from which pool sum is subtracted

        Returns:
        -------
            int: Result of subtraction

        Raises:
        ------
            DiceOperationTypeError: If other is neither int nor Diceable

        Example:
        -------
            >>> from diceroller.aliases import d6
            >>> pool = DicePool([d6(), d6()])
            >>> 10 - pool  # 10 minus pool sum
            3

        """
        if isinstance(other, int):
            return other - sum(self.roll())
        elif isinstance(other, DicePool):
            return sum(other.roll()) - sum(self.roll())
        elif isinstance(other, Dice):
            return other.roll() - sum(self.roll())
        else:
            raise DiceOperationTypeError(f"Cannot subtract Dice with {type(other)}")

    def __mul__(self, other: int | Diceable) -> int:
        """
        Multiply the pool sum by an integer or another Diceable roll sum.

        Args:
        ----
            other: Integer multiplier or Diceable instance

        Returns:
        -------
            int: Multiplied pool sum

        Raises:
        ------
            DiceOperationTypeError: If other is neither int nor Diceable

        Example:
        -------
            >>> from diceroller.aliases import d6
            >>> pool = DicePool([d6(), d6()])
            >>> pool * 2  # Pool sum multiplied by 2
            10
            >>> pool * d6()  # Pool sum multiplied by another d6 roll
            15

        """
        if isinstance(other, int):
            return sum(sum(self.roll()) for _ in range(other))
        elif isinstance(other, DicePool):
            return sum(get_rolls(other)) * sum(get_rolls(self))
        elif isinstance(other, Dice):
            return other.roll() * sum(get_rolls(self))
        else:
            raise DiceOperationTypeError(f"Cannot multiply Dice with {type(other)}")

    def __rmul__(self, other: int | Diceable) -> int:
        """
        Handle right-side multiplication (other * pool sum).

        Args:
        ----
            other: Integer multiplier or Diceable instance

        Returns:
        -------
            int: Multiplied pool sum

        Raises:
        ------
            DiceOperationTypeError: If other is neither int nor Diceable

        Example:
        -------
            >>> from diceroller.aliases import d6
            >>> pool = DicePool([d6(), d6()])
            >>> 2 * pool  # Equivalent to pool * 2
            10

        """
        if isinstance(other, int):
            return sum(sum(self.roll()) for _ in range(other))
        elif isinstance(other, DicePool):
            return sum(other.roll()) * sum(self.roll())
        elif isinstance(other, Dice):
            return other.roll() * sum(self.roll())
        else:
            raise DiceOperationTypeError(f"Cannot multiply Dice with {type(other)}")

    def __iter__(self) -> Generator[Dice, None, None]:
        """
        Iterate over dice in the pool.

        Yields each Dice instance in the pool sequentially.

        Yields:
        ------
            Dice: Individual dice from the pool

        Example:
        -------
            >>> from diceroller.aliases import d6
            >>> pool = DicePool([d6(), d6()])
            >>> for die in pool:
            ...     isinstance(die, Dice)
            True
            True

        """
        yield from self._dice_list

    def __len__(self) -> int:
        """
        Get the number of dice in the pool.

        Returns:
        -------
            int: Count of dice in the pool

        Example:
        -------
            >>> from diceroller.aliases import d6
            >>> pool = DicePool([d6(), d6(), d6()])
            >>> len(pool)
            3

        """
        return len(self._dice_list)

    def __getitem__(self, index: int | slice) -> Dice | list[Dice]:
        """
        Get dice at specified index or slice.

        Supports both single index access and slicing operations.

        Args:
        ----
            index: Position of dice to retrieve (int) or slice range

        Returns:
        -------
            Dice | list[Dice]: Single die for int index, list of dice for slices

        Raises:
        ------
            IndexError: If index is out of range
            TypeError: If index is not int or slice

        Examples:
        --------
            >>> from diceroller.aliases import d6, d20
            >>> pool = DicePool([d6(), d20(), d6()])
            >>> isinstance(pool[0], Dice)
            True
            >>> len(pool[1:3])
            2

        """
        if isinstance(index, int | slice):
            return self._dice_list[index]
        else:
            raise TypeError(f"Indices must be integers or slices, not {type(index).__name__}")

    def __contains__(self, item: Dice) -> bool:
        """
        Check if a specific die exists in the pool.

        Uses identity comparison (is) rather than value equality.

        Args:
        ----
            item: Dice instance to check for membership

        Returns:
        -------
            bool: True if die exists in pool, False otherwise

        Example:
        -------
            >>> from diceroller.aliases import d6
            >>> die = d6()
            >>> pool = DicePool([die, d6()])
            >>> die in pool
            True

        """
        return item in self._dice_list

    def __repr__(self) -> str:
        """
        Get unambiguous string representation of the dice pool.

        Shows class name and contained dice in a reconstructible format.

        Returns:
        -------
            str: Developer-friendly representation

        Example:
        -------
            >>> from diceroller.aliases import d6
            >>> pool = DicePool([d6(), d6()])
            >>> repr(pool)
            'DicePool([Dice(_smallest_side=1, _biggest_side=6, ...), Dice(_smallest_side=1, _biggest_side=6, ...)])'

        """
        dice_reprs = [repr(die) for die in self._dice_list]
        return f"{self.__class__.__name__}([{', '.join(dice_reprs)}])"

    def __str__(self) -> str:
        """
        Get human-readable string representation of the dice pool.

        Shows dice count and side configurations in a compact format.

        Returns:
        -------
            str: User-friendly representation

        Example:
        -------
            >>> from diceroller.aliases import d6, d20
            >>> pool = DicePool([d6(), d20(), d6()])
            >>> str(pool)
            'DicePool(3 dice: [1d6, 1d20, 1d6])'

        """
        dice_notation = []
        current_die = None
        count = 0

        for die in self._dice_list:
            if (
                current_die
                and die._smallest_side == current_die._smallest_side
                and die._biggest_side == current_die._biggest_side
            ):
                count += 1
            else:
                if current_die:
                    dice_notation.append(
                        f"{count}d{current_die._biggest_side}" if count > 1 else f"1d{current_die._biggest_side}"
                    )
                current_die = die
                count = 1

        if current_die:
            dice_notation.append(
                f"{count}d{current_die._biggest_side}" if count > 1 else f"1d{current_die._biggest_side}"
            )

        return f"DicePool({len(self._dice_list)} dice: [{', '.join(dice_notation)}])"
