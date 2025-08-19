from src.diceroller import Dice
from src.diceroller.strategies import DefaultRoll, DisadvantageRoll, AdvantageRoll, MultipleRoll
import pytest


@pytest.fixture()
def create_dice() -> Dice:
    return Dice(1, 20)


def test_check_random(create_dice) -> bool:
    dice_object = create_dice
    assert 1 <= dice_object.roll() <= 20


def test_dice_check_success(create_dice) -> bool:
    assert create_dice.check_success(check=0)


@pytest.mark.parametrize("smallest_side, biggest_side", [(0, 0), (10, 0), (-1, 10), (1, -10)])
def test_dice_valueError(smallest_side, biggest_side) -> bool:
    with pytest.raises(ValueError):
        assert Dice(smallest_side, biggest_side)


@pytest.mark.parametrize(
    "inserted_strategy",
    [
        (DefaultRoll()),
        (DisadvantageRoll()),
        (AdvantageRoll()),
        (MultipleRoll(times=1)),
    ],
)
def test_dice_roll_with_inserted_strategy(inserted_strategy, create_dice):
    assert 1 <= create_dice.roll(inserted_roll_strategy=inserted_strategy) <= 20
