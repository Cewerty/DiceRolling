from ..dice import Dice  # noqa: D100
from ..strategies import DefaultRandomStrategy, DefaultRoll, RandomStrategy, RollStrategy


def d4(*, _random_strategy: RandomStrategy | None = None, _roll_strategy: RollStrategy | None = None) -> Dice:
    """
    Create a standard 4-sided die (d4).

    Args:
    ----
        random_strategy (RandomStrategy): Random number generation strategy
        roll_strategy (RollStrategy): Dice rolling strategy

    Returns:
    -------
        Dice: 4-sided die (1-4)

    """
    if _random_strategy is None:
        _random_strategy = DefaultRandomStrategy()
    if _roll_strategy is None:
        _roll_strategy = DefaultRoll()
    return Dice(1, 4, _random_strategy, _roll_strategy)


def d6(*, _random_strategy: RandomStrategy | None = None, _roll_strategy: RollStrategy | None = None) -> Dice:
    """
    Create a standard 6-sided die (d6).

    Args:
    ----
        random_strategy (RandomStrategy): Random number generation strategy
        roll_strategy (RollStrategy): Dice rolling strategy

    Returns:
    -------
        Dice: 6-sided die (1-6)

    """
    if _random_strategy is None:
        _random_strategy = DefaultRandomStrategy()
    if _roll_strategy is None:
        _roll_strategy = DefaultRoll()
    return Dice(1, 6, _random_strategy, _roll_strategy)


def d8(*, _random_strategy: RandomStrategy | None = None, _roll_strategy: RollStrategy | None = None) -> Dice:
    """
    Create a standard 8-sided die (d8).

    Args:
    ----
        random_strategy (RandomStrategy): Random number generation strategy
        roll_strategy (RollStrategy): Dice rolling strategy

    Returns:
    -------
        Dice: 8-sided die (1-8)

    """
    if _random_strategy is None:
        _random_strategy = DefaultRandomStrategy()
    if _roll_strategy is None:
        _roll_strategy = DefaultRoll()
    return Dice(1, 8, _random_strategy, _roll_strategy)


def d10(*, _random_strategy: RandomStrategy | None = None, _roll_strategy: RollStrategy | None = None) -> Dice:
    """
    Create a standard 10-sided die (d10).

    Args:
    ----
        random_strategy (RandomStrategy): Random number generation strategy
        roll_strategy (RollStrategy): Dice rolling strategy

    Returns:
    -------
        Dice: 10-sided die (1-10)

    Note:
    ----
        Use this d10 for regular rolls in RPGs

    """
    if _random_strategy is None:
        _random_strategy = DefaultRandomStrategy()
    if _roll_strategy is None:
        _roll_strategy = DefaultRoll()
    return Dice(1, 10, _random_strategy, _roll_strategy)


def d10_percentages(
    *, _random_strategy: RandomStrategy | None = None, _roll_strategy: RollStrategy | None = None
) -> Dice:
    """
    Create a standard 10-sided die (d10) with RPG-specific range.

    Args:
    ----
        random_strategy (RandomStrategy): Random number generation strategy
        roll_strategy (RollStrategy): Dice rolling strategy

    Returns:
    -------
        Dice: 10-sided die (0-9)

    Note:
    ----
        Uses 0-9 range for compatibility with percentile dice systems in RPGs

    """
    if _random_strategy is None:
        _random_strategy = DefaultRandomStrategy()
    if _roll_strategy is None:
        _roll_strategy = DefaultRoll()
    return Dice(0, 9, _random_strategy, _roll_strategy)


def d12(*, _random_strategy: RandomStrategy | None = None, _roll_strategy: RollStrategy | None = None) -> Dice:
    """
    Create a standard 12-sided die (d12).

    Args:
    ----
        random_strategy (RandomStrategy): Random number generation strategy
        roll_strategy (RollStrategy): Dice rolling strategy

    Returns:
    -------
        Dice: 12-sided die (1-12)

    """
    if _random_strategy is None:
        _random_strategy = DefaultRandomStrategy()
    if _roll_strategy is None:
        _roll_strategy = DefaultRoll()
    return Dice(1, 12, _random_strategy, _roll_strategy)


def d20(*, _random_strategy: RandomStrategy | None = None, _roll_strategy: RollStrategy | None = None) -> Dice:
    """
    Create a standard 20-sided die (d20).

    Args:
    ----
        random_strategy (RandomStrategy): Random number generation strategy
        roll_strategy (RollStrategy): Dice rolling strategy

    Returns:
    -------
        Dice: 20-sided die (1-20)

    """
    if _random_strategy is None:
        _random_strategy = DefaultRandomStrategy()
    if _roll_strategy is None:
        _roll_strategy = DefaultRoll()
    return Dice(1, 20, _random_strategy, _roll_strategy)


def custom_dice(
    smallest_side: int = 1,
    biggest_side: int = 4,
    random_strategy: RandomStrategy | None = None,
    roll_strategy: RollStrategy | None = None,
) -> Dice:
    """
    Create a single die with specified parameters.

    Args:
    ----
        smallest_side(int): Smallest face value of the die
        biggest_side(int): Largest face value of the die
        random_strategy (RandomStrategy): Random number generation strategy
        roll_strategy (RollStrategy): Dice rolling strategy

    Returns:
    -------
        Configured Dice instance

    """
    if random_strategy is None:
        random_strategy = DefaultRandomStrategy()
    if roll_strategy is None:
        roll_strategy = DefaultRoll()
    return Dice(smallest_side, biggest_side, random_strategy, roll_strategy)
