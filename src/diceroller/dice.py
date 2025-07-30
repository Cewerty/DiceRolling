"""
Module containing dice-related logic.

Contains:
- Dice class

Example usage:
>>> dice = Dice(1, 20)
>>> dice.roll()
15
>>> dice.check_success(10)
True

"""

from dataclasses import dataclass, field
from typing import Final

from .dice_strategies import (
    DefaultRandomStrategy,
    DefaultRoll,
    RandomStrategy,
    RollStrategy,
)


@dataclass(slots=True, frozen=True)
class Dice:
    """
    Class for immutable dice.

    Attributes:
        _smallest_side (int): Smallest side of the die
        _biggest_side (int): Largest side of the die
        _randomization_strategy (RandomStrategy): Random number generation strategy
        _roll_strategy (RollStrategy): Dice rolling strategy

    Raises:
        ValueError: If smallest side is larger than biggest side or negative

    """

    _smallest_side: Final[int]
    _biggest_side: Final[int]
    _randomization_strategy: Final[RandomStrategy] = field(default_factory=DefaultRandomStrategy)
    _roll_strategy: Final[RollStrategy] = field(default_factory=DefaultRoll)

    def __post_init__(self) -> None:
        """
        Initialize dice side validation.

        Raises:
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
            int: Smallest side value (read-only)

        Note:
            Value is set during instance creation

        """
        return self._smallest_side

    @property
    def biggest_side(self) -> int:
        """
        Get the largest side of the die.

        Returns:
            int: Largest side value (read-only)

        Note:
            Value is set during instance creation

        """
        return self._biggest_side

    @property
    def randomization_strategy(self) -> RandomStrategy:
        """
        Get the random number generation strategy.

        Returns:
            RandomStrategy: Randomization strategy instance

        Note:
            Value is set during instance creation

        """
        return self._randomization_strategy

    @property
    def roll_strategy(self) -> RollStrategy:
        """
        Get the dice rolling strategy.

        Returns:
            RollStrategy: Roll strategy instance

        Note:
            Value is set during instance creation

        """
        return self._roll_strategy

    def check_success(self, check: int, inserted_roll_strategy: RollStrategy | None = None) -> bool:
        """
        Check success against a target number.

        Args:
            check: Target number to beat
            inserted_roll_strategy: Optional roll strategy override

        Returns:
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
            modifier: Roll modifier to add
            inserted_roll_strategy: Optional roll strategy override

        Returns:
            int: Final roll result

        """
        if inserted_roll_strategy is None:
            return self.roll_strategy.roll(self, modifier)
        return inserted_roll_strategy.roll(self, modifier)
