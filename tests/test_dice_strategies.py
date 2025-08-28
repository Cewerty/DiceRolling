from src.diceroller import Dice
from src.diceroller.strategies import DefaultRoll, DisadvantageRoll, AdvantageRoll, MultipleRoll, RollStrategy
from typing import Hashable
import pytest
from typing import Tuple


@pytest.fixture
def create_same_Multiple_Rolls() -> Tuple[MultipleRoll, MultipleRoll]:
    return MultipleRoll(1), MultipleRoll(1)


@pytest.fixture
def create_different_Multiple_Rolls() -> Tuple[MultipleRoll, MultipleRoll]:
    return MultipleRoll(1), MultipleRoll(2)


def test_multiple_roll_cache_clear(create_same_Multiple_Rolls: Tuple[MultipleRoll, MultipleRoll]) -> None:
    first: MultipleRoll = create_same_Multiple_Rolls[0]
    second: MultipleRoll = create_same_Multiple_Rolls[1]
    MultipleRoll.clear_instances()
    assert len(MultipleRoll._instances) == 0


def test_multiple_roll_cache(create_same_Multiple_Rolls: Tuple[MultipleRoll, MultipleRoll]) -> None:
    first: MultipleRoll = create_same_Multiple_Rolls[0]
    second: MultipleRoll = create_same_Multiple_Rolls[1]
    assert first is second


def test_multiple_roll_is_hashable(create_same_Multiple_Rolls: Tuple[MultipleRoll, MultipleRoll]) -> None:
    assert isinstance(create_same_Multiple_Rolls[0], Hashable)


def test_multiple_roll_hash(create_same_Multiple_Rolls: Tuple[MultipleRoll, MultipleRoll]) -> None:
    first: MultipleRoll = create_same_Multiple_Rolls[0]
    hashed_first = hash(first)
    Roll_dict = {hashed_first: "MultipleRoll"}
    assert Roll_dict[hashed_first] == "MultipleRoll"


def test_multiple_roll_eq_hash(create_same_Multiple_Rolls: Tuple[MultipleRoll, MultipleRoll]) -> None:
    assert hash(create_same_Multiple_Rolls[0]) == hash(create_same_Multiple_Rolls[1])


def test_multiple_roll_not_eq_hash(create_different_Multiple_Rolls: Tuple[MultipleRoll, MultipleRoll]) -> None:
    first: MultipleRoll = create_different_Multiple_Rolls[0]
    second: MultipleRoll = create_different_Multiple_Rolls[1]
    assert hash(first) != hash(second)


def test_multiple_roll_in_set(create_same_Multiple_Rolls: Tuple[MultipleRoll, MultipleRoll]) -> None:
    assert len({create_same_Multiple_Rolls[0], create_same_Multiple_Rolls[1]}) == 1


def test_multiple_roll_eq(create_same_Multiple_Rolls: Tuple[MultipleRoll, MultipleRoll]) -> None:
    assert create_same_Multiple_Rolls[0] == create_same_Multiple_Rolls[1]


def test_multiple_roll_error_eq(create_different_Multiple_Rolls: Tuple[MultipleRoll, MultipleRoll]) -> None:
    with pytest.raises(NotImplementedError):
        assert create_different_Multiple_Rolls[0] == 1
