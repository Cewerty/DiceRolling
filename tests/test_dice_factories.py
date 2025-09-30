from src.diceroller.factories import DiceFactory
from src.diceroller.strategies import PseudoRandomStrategy
from src.diceroller.dice import Dice
import pytest
from typing_extensions import Callable, Tuple


@pytest.fixture
def create_dice_factory() -> DiceFactory:
    return DiceFactory()


def test_create_dice_set(create_dice_factory: DiceFactory) -> None:
    dice_dict = create_dice_factory._make_dice_set()
    assert dice_dict.items() != 0


@pytest.mark.parametrize("smallest_side, biggest_side", [(1, 4), (1, 6), (1, 8), (1, 10), (1, 12), (1, 20)])
def test_create_dice_using_factory(smallest_side: int, biggest_side: int, create_dice_factory: DiceFactory) -> None:
    dice = create_dice_factory._make_dice(smallest_side, biggest_side)
    assert isinstance(dice, Dice)

    assert (
        dice.biggest_side == biggest_side
        and dice.smallest_side == smallest_side
        and dice.smallest_side <= dice.roll() <= dice.biggest_side
    )


def test_creation_of_dice_factories_with_class() -> None:
    assert isinstance(DiceFactory(PseudoRandomStrategy), DiceFactory)


def test_creation_of_dice_factories_with_object() -> None:
    assert isinstance(DiceFactory(PseudoRandomStrategy()), DiceFactory)
