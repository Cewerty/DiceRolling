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


@pytest.mark.parametrize(
    "factory_method, expected_range",
    [
        (lambda f: f.d4(), (1, 4)),
        (lambda f: f.d6(), (1, 6)),
        (lambda f: f.d8(), (1, 8)),
        (lambda f: f.d10(), (1, 10)),
        (lambda f: f.d10_percentages(), (0, 9)),
        (lambda f: f.d12(), (1, 12)),
        (lambda f: f.d20(), (1, 20)),
    ],
    ids=["d4", "d6", "d8", "d10", "d10_percentages", "d12", "d20"],
)
def test_factory_methods(
    create_dice_factory: DiceFactory, factory_method: Callable[[DiceFactory], Dice], expected_range: Tuple[int, int]
) -> None:
    """
    Test all factory methods to ensure they create dice with correct ranges.

    Args:
        create_dice_factory: Fixture providing a DiceFactory instance
        factory_method: Lambda function that calls the factory method
        expected_range: Tuple of (min_value, max_value) for the die
    """
    factory: DiceFactory = create_dice_factory
    dice: Dice = factory_method(factory)

    min_val, max_val = expected_range

    # Test that the dice has correct attributes
    assert dice.smallest_side == min_val
    assert dice.biggest_side == max_val


def test_creation_of_dice_factories_with_class() -> None:
    assert isinstance(DiceFactory(PseudoRandomStrategy), DiceFactory)


def test_creation_of_dice_factories_with_object() -> None:
    assert isinstance(DiceFactory(PseudoRandomStrategy()), DiceFactory)
