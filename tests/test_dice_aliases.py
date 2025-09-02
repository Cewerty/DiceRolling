from src.diceroller.aliases import d4, d6, d8, d10, d10_percentages, d12, d20, custom_dice
import pytest
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


def test_d4() -> None:
    die: Dice = d4()
    assert (die.smallest_side == 1 and die.biggest_side == 4) and (1 <= die.roll() <= 4)


def test_d6() -> None:
    die: Dice = d6()
    assert (die.smallest_side == 1 and die.biggest_side == 6) and (1 <= die.roll() <= 6)


def test_d8() -> None:
    die: Dice = d8()
    assert (die.smallest_side == 1 and die.biggest_side == 8) and (1 <= die.roll() <= 8)


def test_d10() -> None:
    die: Dice = d10()
    assert (die.smallest_side == 1 and die.biggest_side == 10) and (1 <= die.roll() <= 10)


def test_d10_percentages() -> None:
    die: Dice = d10_percentages()
    assert (die.smallest_side == 0 and die.biggest_side == 9) and (0 <= die.roll() <= 9)


def test_d12() -> None:
    die: Dice = d12()
    assert (die.smallest_side == 1 and die.biggest_side == 12) and (1 <= die.roll() <= 12)


def test_d20() -> None:
    die: Dice = d20()
    assert (die.smallest_side == 1 and die.biggest_side == 20) and (1 <= die.roll() <= 20)


@pytest.mark.parametrize(
    "smallest_side,biggest_side,random_strategy,roll_strategy",
    [
        (0, 4, DefaultRandomStrategy(), DefaultRoll()),
        (0, 6, PseudoRandomStrategy(), MultipleRoll()),
        (0, 8, PseudoRandomStrategy(), AdvantageRoll()),
        (0, 10, PseudoRandomStrategy(), DisadvantageRoll()),
        (0, 12, None, None),
    ],
)
def test_custom_dice(
    smallest_side: int, biggest_side: int, random_strategy: RandomStrategy, roll_strategy: RollStrategy
) -> None:
    die: Dice = custom_dice(smallest_side, biggest_side, random_strategy, roll_strategy)
    assert (die.smallest_side == smallest_side and die.biggest_side == biggest_side) and (
        smallest_side <= die.roll() <= biggest_side
    )
