import pytest
from functools import partial
from typing import Callable, Optional

from src.diceroller.aliases import d4, d6, d8, d10, d10_percentages, d12, d20, create_dice
from src.diceroller.dice import Dice
from src.diceroller.strategies import (
    RollStrategy,
    DefaultRoll,
    MultipleRoll,
    AdvantageRoll,
    DisadvantageRoll,
    RandomStrategy,
    PseudoRandomStrategy,
    DefaultRandomStrategy,
)

DiceFactory = Callable[..., Dice]


@pytest.mark.parametrize(
    "dice_factory,expected_min,expected_max",
    [
        (d4, 1, 4),
        (d6, 1, 6),
        (d8, 1, 8),
        (d10, 1, 10),
        (d10_percentages, 0, 9),
        (d12, 1, 12),
        (d20, 1, 20),
    ],
)
@pytest.mark.parametrize(
    "roll_strategy,random_strategy",
    [
        (None, None),
        (DefaultRoll(), DefaultRandomStrategy()),
        (MultipleRoll(), PseudoRandomStrategy()),
        (AdvantageRoll(), PseudoRandomStrategy()),
        (DisadvantageRoll(), PseudoRandomStrategy()),
    ],
)
def test_all_dice_partials(
    dice_factory: DiceFactory,
    expected_min: int,
    expected_max: int,
    roll_strategy: Optional[RollStrategy],
    random_strategy: Optional[RandomStrategy],
) -> None:
    die = dice_factory(_random_strategy=random_strategy, _roll_strategy=roll_strategy)

    assert die.smallest_side == expected_min
    assert die.biggest_side == expected_max
    assert isinstance(die, Dice)

    if random_strategy is None:
        assert isinstance(die.randomization_strategy, DefaultRandomStrategy)
    else:
        assert die.randomization_strategy is random_strategy

    if roll_strategy is None:
        assert isinstance(die.roll_strategy, DefaultRoll)
    else:
        assert die.roll_strategy is roll_strategy

    roll_result = die.roll()
    assert expected_min <= roll_result <= expected_max


@pytest.mark.parametrize(
    "smallest_side,biggest_side,random_strategy,roll_strategy",
    [
        (1, 4, DefaultRandomStrategy(), DefaultRoll()),
        (1, 6, PseudoRandomStrategy(), MultipleRoll()),
        (1, 8, PseudoRandomStrategy(), AdvantageRoll()),
        (1, 10, PseudoRandomStrategy(), DisadvantageRoll()),
        (1, 12, None, None),
    ],
)
def test_create_dice(
    smallest_side: int,
    biggest_side: int,
    random_strategy: Optional[RandomStrategy],
    roll_strategy: Optional[RollStrategy],
) -> None:
    die: Dice = create_dice(
        smallest_side,
        biggest_side,
        _random_strategy=random_strategy,
        _roll_strategy=roll_strategy,
    )

    assert die.smallest_side == smallest_side
    assert die.biggest_side == biggest_side

    if random_strategy is None:
        assert isinstance(die.randomization_strategy, DefaultRandomStrategy)
    else:
        assert die.randomization_strategy is random_strategy

    if roll_strategy is None:
        assert isinstance(die.roll_strategy, DefaultRoll)
    else:
        assert die.roll_strategy is roll_strategy

    assert smallest_side <= die.roll() <= biggest_side
