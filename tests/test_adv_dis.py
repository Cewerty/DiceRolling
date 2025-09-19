from random import randint
from src.diceroller.dice import Dice
import pytest
from src.diceroller.dice import adv, dis
from typing import List, cast


@pytest.fixture
def get_dice() -> Dice:
    return Dice(1, 4)


def test_adv_with_correct_list(get_dice: Dice) -> None:
    dice_list = cast(List[Dice], [get_dice for _ in range(5)])
    assert 1 <= adv(dice_list) <= 4


def test_adv_with_correct_dice(get_dice: Dice) -> None:
    assert 1 <= adv(get_dice) <= 4


def test_adv_with_incorrect_objects() -> None:
    with pytest.raises(TypeError):
        incorrect_list = cast(List[Dice], [randint(1, 4) for _ in range(5)])
        adv(incorrect_list)


def test_adv_with_incorrect_object() -> None:
    with pytest.raises(TypeError):
        incorrect_dice = cast(Dice, 1)
        adv(incorrect_dice)


def test_dis_with_correct_list(get_dice: Dice) -> None:
    dice_list = cast(List[Dice], [get_dice for _ in range(5)])
    assert 1 <= dis(dice_list) <= 4


def test_dis_with_correct_dice(get_dice: Dice) -> None:
    assert 1 <= dis(get_dice) <= 4


def test_dis_with_incorrect_objects() -> None:
    with pytest.raises(TypeError):
        incorrect_list = cast(List[Dice], [randint(1, 4) for _ in range(5)])
        dis(incorrect_list)


def test_dis_with_incorrect_object() -> None:
    with pytest.raises(TypeError):
        incorrect_dice = cast(Dice, 1)
        dis(incorrect_dice)
