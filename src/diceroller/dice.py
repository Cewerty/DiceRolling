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
    * Implement dice pool strategies
    * Add operations support

"""

from __future__ import annotations

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

    def __radd__(self, other: int) -> int:
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

    def __mul__(self, other: int | Dice) -> list[Dice]:
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
            return [deepcopy(self) for _ in range(other)]
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
