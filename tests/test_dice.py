from src.diceroller import Dice
from src.diceroller.strategies import DefaultRoll, DisadvantageRoll, AdvantageRoll, MultipleRoll, RollStrategy
import pytest
from src.diceroller.strategies import DefaultRandomStrategy, PseudoRandomStrategy, RandomStrategy


@pytest.fixture()
def create_dice() -> Dice:
    """Fixture to create a standard 20-sided die for testing."""
    return Dice(1, 20)


def test_check_random(create_dice: Dice) -> None:
    """Test that dice roll returns a value within the valid range."""
    dice_object = create_dice
    assert 1 <= dice_object.roll() <= 20


def test_dice_check_success(create_dice: Dice) -> None:
    """Test that check_success method works correctly with threshold 0."""
    assert create_dice.check_success(check=0)


@pytest.mark.parametrize("smallest_side, biggest_side", [(0, 0), (10, 0), (-1, 10), (1, -10)])
def test_dice_valueError(smallest_side: int, biggest_side: int) -> None:
    """
    Test that Dice constructor raises ValueError for invalid side values.

    Args:
        smallest_side: Invalid smallest side values to test
        biggest_side: Invalid biggest side values to test

    Test cases cover:
    - Both sides equal to zero
    - Smallest side larger than biggest side
    - Negative smallest side
    - Negative biggest side
    """
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
def test_dice_roll_with_inserted_strategy(inserted_strategy: RollStrategy, create_dice: Dice) -> None:
    """
    Test that dice roll works correctly with various roll strategies.

    Args:
        inserted_strategy: The roll strategy to test
        create_dice: Fixture providing a Dice instance

    Verifies that all strategy types produce valid roll results within expected range.
    """
    assert 1 <= create_dice.roll(inserted_roll_strategy=inserted_strategy) <= 20


@pytest.mark.parametrize("random_strategy", [(DefaultRandomStrategy()), (PseudoRandomStrategy())])
def test_create_dice_with_different_random_strategies(random_strategy: RandomStrategy) -> None:
    """
    Test that Dice works correctly with different randomization strategies.

    Args:
        random_strategy: The randomization strategy to test

    Ensures that both default and pseudo-random strategies produce valid results.
    """
    dice_object = Dice(1, 20, random_strategy)
    assert 1 <= dice_object.roll() <= 20
