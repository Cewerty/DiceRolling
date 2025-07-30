"""
Module containing randomization and dice-rolling strategies for RPG dice systems.

Provides implementations of:
- Random number generation strategies (cryptographic, pseudo-random, NumPy-based)
- Dice rolling strategies (standard, advantage, disadvantage, multiple rolls)
- Optimized multiple roll strategy with instance caching

Classes:
    RandomStrategy: Protocol for random number generators
    DefaultRandomStrategy: Cryptographically strong random numbers
    PseudoRandomStrategy: Standard pseudo-random generator
    NumPyStrategy: NumPy-based random generator
    RollStrategy: Protocol for dice rolling strategies
    DefaultRoll: Standard single die roll
    DisadvantageRoll: Roll two dice take lowest
    AdvantageRoll: Roll two dice take highest
    MultipleRoll: Roll multiple dice and sum (with instance caching)

Example:
    >>> from dice_strategies import DefaultRandomStrategy, DefaultRoll
    >>> from dice import Dice
    >>> die = Dice(1, 20, DefaultRandomStrategy(), DefaultRoll())
    >>> result = die.roll()
    >>> 1 <= result <= 20
    True

"""

from __future__ import annotations

import random
from collections.abc import Generator
from dataclasses import dataclass
from secrets import SystemRandom
from typing import TYPE_CHECKING, ClassVar, Protocol
from weakref import WeakValueDictionary

import numpy as np

if TYPE_CHECKING:
    from .dice import Dice


class RandomStrategy(Protocol):
    """Protocol for random number generation strategies."""

    def randint(self, smallest: int, biggest: int) -> int:
        """
        Generate a random integer between smallest and biggest (inclusive).

        Args:
            smallest: Lower bound (inclusive)
            biggest: Upper bound (inclusive)

        Returns:
            Random integer in range [smallest, biggest]

        """


class DefaultRandomStrategy:
    """Cryptographically strong random number strategy using system RNG."""

    def __init__(self) -> None:
        """Initialize the strategy with a secure random number generator."""
        self._systemRandom: SystemRandom = SystemRandom()

    def randint(self, smallest: int, biggest: int) -> int:
        """
        Generate a cryptographically strong random integer.

        Args:
            smallest: Lower bound (inclusive)
            biggest: Upper bound (inclusive)

        Returns:
            Secure random integer in range [smallest, biggest]

        """
        return self._systemRandom.randint(a=smallest, b=biggest)


class PseudoRandomStrategy:
    """Standard pseudo-random number strategy using Python's random module."""

    def randint(self, smallest: int, biggest: int) -> int:
        """
        Generate a pseudo-random integer.

        Args:
            smallest: Lower bound (inclusive)
            biggest: Upper bound (inclusive)

        Returns:
            Pseudo-random integer in range [smallest, biggest]

        Note:
            Not suitable for cryptographic purposes

        """
        return random.randint(smallest, biggest)  # noqa: S311


class NumPyStrategy:
    """Random number strategy using NumPy's Generator interface."""

    def __init__(self) -> None:
        """Initialize the strategy with NumPy's default random generator."""
        self._rng: Generator = np.random.default_rng()

    def randint(self, smallest: int, biggest: int) -> int:
        """
        Generate a random integer using NumPy's generator.

        Args:
            smallest: Lower bound (inclusive)
            biggest: Upper bound (inclusive)

        Returns:
            Random integer in range [smallest, biggest]

        """
        return int(self._rng.integers(smallest, biggest + 1))


class RollStrategy(Protocol):
    """Protocol for dice rolling strategies."""

    def roll(self, dice: Dice, modifier: int = 0) -> int:
        """
        Execute a dice roll with optional modifier.

        Args:
            dice: Dice instance to roll
            modifier: Modifier to add to the result (default 0)

        Returns:
            Result of the dice roll with modifier applied

        """


class DefaultRoll:
    """Standard single-die rolling strategy."""

    def roll(self, dice: Dice, modifier: int = 0) -> int:
        """
        Roll a single die and apply modifier.

        Args:
            dice: Dice instance to roll
            modifier: Modifier to add to the result

        Returns:
            Single die roll result + modifier

        """
        return (dice.randomization_strategy.randint(dice.smallest_side, dice.biggest_side)) + modifier


class DisadvantageRoll:
    """Roll strategy that takes the lowest of two dice rolls."""

    def roll(self, dice: Dice, modifier: int = 0) -> int:
        """
        Roll two dice and take the lowest result.

        Args:
            dice: Dice instance to roll
            modifier: Modifier to add to the result

        Returns:
            Lowest roll result + modifier

        """
        first_roll = dice.randomization_strategy.randint(dice.smallest_side, dice.biggest_side)
        second_roll = dice.randomization_strategy.randint(dice.smallest_side, dice.biggest_side)
        return min(first_roll, second_roll) + modifier


class AdvantageRoll:
    """Roll strategy that takes the highest of two dice rolls."""

    def roll(self, dice: Dice, modifier: int = 0) -> int:
        """
        Roll two dice and take the highest result.

        Args:
            dice: Dice instance to roll
            modifier: Modifier to add to the result

        Returns:
            Highest roll result + modifier

        """
        first_roll = dice.randomization_strategy.randint(dice.smallest_side, dice.biggest_side)
        second_roll = dice.randomization_strategy.randint(dice.smallest_side, dice.biggest_side)
        return max(first_roll, second_roll) + modifier


@dataclass(frozen=True, slots=True)
class MultipleRoll:
    """Roll strategy for multiple dice with instance caching."""

    times: int
    _instances: ClassVar[WeakValueDictionary[int, MultipleRoll]] = WeakValueDictionary()

    def __hash__(self) -> int:
        """
        Generate a hash value based on the number of rolls.

        Returns:
            Hash value of the times attribute

        Note:
            Supports usage in hashable collections (dicts, sets).
        
        """
        return hash(self.times)

    def __eq__(self, other: MultipleRoll) -> bool:
        """
        Compare instances for equality based on roll count.

        Args:
            other: Another instance to compare with

        Returns:
            True if both are MultipleRoll instances with same times value

        Note:
            Enables value-based comparison instead of instance identity.
        
        """
        return isinstance(other, MultipleRoll) and other.times == self.times

    def __new__(cls, times: int = 1) -> MultipleRoll:
        """
        Create or retrieve a cached instance for the specified number of rolls.

        Args:
            times: Number of dice to roll

        Returns:
            Cached or new MultipleRoll instance

        Example:
            >>> a = MultipleRoll(3)
            >>> b = MultipleRoll(3)
            >>> a is b
            True
        
        """
        if times in cls._instances:
            return cls._instances[times]
        self = super().__new__()
        object.__setattr__(self, "_times", times)
        cls._instances[times] = self
        return self

    @classmethod
    def clear_instances(cls) -> None:
        """
        Clear all cached instances of the class.

        Note:
            Useful for resetting the instance cache during runtime.
            
        """
        cls._instances.clear()

    @property
    def times(self) -> int:
        """
        Get the number of dice to roll.

        Returns:
            Number of dice (read-only)
        
        """
        return self._times

    def roll(self, dice: Dice, modifier: int = 0) -> int:
        """
        Roll multiple dice and sum the results.

        Args:
            dice: Dice instance to roll
            modifier: Modifier to add to the total

        Returns:
            Sum of all dice rolls + modifier

        Example:
            >>> strategy = MultipleRoll(3)
            >>> d6 = Dice(1, 6)
            >>> result = strategy.roll(d6)
            >>> 3 <= result <= 18
            True
        
        """
        return (
            sum(dice.randomization_strategy.randint(dice.smallest_side, dice.biggest_side) for _ in range(self.times))
            + modifier
        )
