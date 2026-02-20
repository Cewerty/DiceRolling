from src.diceroller.dice import Dice, DicePool


class FixedRandomStrategy:
    """Simple deterministic strategy for predictable pool arithmetic tests."""

    def __init__(self, value: int) -> None:
        self._value = value

    def randint(self, smallest: int, biggest: int) -> int:
        return self._value


def _fixed_die(value: int = 3) -> Dice:
    return Dice(1, 6, _randomization_strategy=FixedRandomStrategy(value))


def test_pool_roll_returns_raw_rolls_without_per_die_modifier() -> None:
    pool = DicePool([_fixed_die(2), _fixed_die(4)])

    assert pool.roll(modifier=100) == [2, 4]


def test_pool_add_integer_applies_modifier_to_total_once() -> None:
    pool = DicePool([_fixed_die(2), _fixed_die(4)])

    assert pool + 3 == 9
    assert 3 + pool == 9


def test_pool_subtract_semantics_match_left_operand() -> None:
    pool = DicePool([_fixed_die(2), _fixed_die(4)])

    assert pool - 1 == 5
    assert pool - _fixed_die(5) == 1
    assert 5 - pool == -1


def test_pool_to_pool_subtraction_uses_correct_direction() -> None:
    left = DicePool([_fixed_die(4), _fixed_die(4)])
    right = DicePool([_fixed_die(2), _fixed_die(2)])

    assert left - right == 4
    assert right - left == -4
