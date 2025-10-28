"""Factory method for DicePool class."""

from ..dice import Dice, DicePool, _to_dice_list


def create_dicepool(dice_list: list[Dice] | Dice) -> DicePool:
    """
    Create a DicePool instance from a single die or list of dice.

    Normalizes input into a flat list of Dice instances and wraps them in a DicePool.
    Handles nested structures by recursively flattening lists and DicePool instances.

    Args:
    ----
        dice_list: Single Dice instance or list of Dice instances (may include nested lists)

    Returns:
    -------
        DicePool: New DicePool containing all normalized dice

    Raises:
    ------
        InvalidDiceInputError: If input contains non-Dice items

    Example:
    -------
        >>> from diceroller.aliases import d6, d20
        >>> pool1 = create_dicepool(d6())  # Single die
        >>> len(pool1) == 1
        True
        >>> pool2 = create_dicepool([d6(), d20(), [d6(), d6()]])  # Nested lists
        >>> len(pool2) == 4
        True

    """
    return DicePool(_to_dice_list(dice_list))
