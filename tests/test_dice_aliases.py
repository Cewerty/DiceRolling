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
from typing import TypeVar, Callable, Optional


# Создаем TypeVar для фабричных функций Dice
DiceFunction = TypeVar("DiceFunction", bound=Callable[..., Dice])


# Теперь используем его в параметризованных тестах
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
def test_all_dice_factories(
    dice_factory: DiceFunction,
    expected_min: int,
    expected_max: int,
    roll_strategy: Optional[RollStrategy],
    random_strategy: Optional[RandomStrategy],
):
    die = dice_factory(_random_strategy=random_strategy, _roll_strategy=roll_strategy)
    assert die.smallest_side == expected_min
    assert die.biggest_side == expected_max
    assert isinstance(die, Dice)
    roll_result = die.roll()
    assert expected_min <= roll_result <= expected_max


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
