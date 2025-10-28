"""
DnD5 dice notation parser module.

This module provides functionality to parse DnD5-style dice notation strings
(e.g., "2d6+3", "4d6kh3") into structured roll objects compatible with the
diceroller library. It uses Lark as the parsing engine and integrates seamlessly
with Dice and DicePool classes.

Provides:
    parse_dice_notation: Function to parse notation into ParsedRoll
    ParsedRoll: Dataclass representing parsed dice expression and modifier

Example:
-------
    Parsing and rolling a standard DnD5 expression::

        >>> from diceroller.utils.parser import parse_dice_notation
        >>> result = parse_dice_notation("2d6+3")
        >>> rolls = result.result.roll(modifier=result.modifier)
        >>> len(rolls) == 2
        True
        >>> sum(rolls) >= 5  # Minimum possible: 1+1+3 = 5
        True

    Using roll modifiers like keep highest::

        >>> result = parse_dice_notation("4d6kh3")
        >>> rolls = result.result.roll()
        >>> len(rolls) == 3  # Keeps only 3 highest out of 4
        True

Note:
----
    Actual roll results are random. For reproducible documentation examples:
    - Use fixed seed in tests
    - Or mark with ``# doctest: +SKIP``

Warning:
-------
    Invalid notation (e.g., "2d6 - d4") raises ValueError.
    Only DnD5-compatible syntax is supported.

Attributes:
----------
    __version__: Module version string (inherited from parent package)

"""
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

from lark import Lark, Token, Transformer, Tree, v_args

from ...aliases import create_dice
from ...dice import DicePool, dh, dl, kh, kl

if TYPE_CHECKING:
    from collections.abc import Iterator


@dataclass(frozen=True, slots=True)
class ParsedRoll:
    """
    Result of parsing a DnD5 dice notation string.

    Contains the dice pool representing the dice expression
    and an integer modifier (e.g., +3 in "2d6+3").

    Attributes
    ----------
        result (DicePool): Dice pool constructed from the notation
        modifier (int): Numeric modifier to apply to the roll result

    """

    result: DicePool
    modifier: int


class DiceTransformer(Transformer[Token, ParsedRoll]):
    """Lark transformer that converts parsed AST into diceroller objects."""

    @v_args(inline=True)
    def start(self, expr: ParsedRoll) -> ParsedRoll:
        """
        Return the top-level expression result.

        Args:
        ----
            expr: Fully processed parsed roll expression

        Returns:
        -------
            The final parsed roll result

        """
        return expr

    @v_args(inline=True)
    def expr(self, first_term: ParsedRoll, *args: Any) -> ParsedRoll:  # noqa: ANN401
        """
        Process arithmetic expressions with dice pools and modifiers.

        Handles expressions like "2d6 + 3" or "4d6kh3 - 1".

        Args:
        ----
            first_term: The first term in the expression (always a ParsedRoll)
            *args: Alternating sequence of operators and terms

        Returns:
        -------
            Combined ParsedRoll with aggregated dice pool and modifier

        Raises:
        ------
            ValueError: If attempting to subtract dice pools (not allowed in DnD5)

        """
        pool = first_term.result
        modifier = first_term.modifier

        # Process operator-term pairs: ("+", term2, "-", term3, ...)
        it: Iterator[Any] = iter(args)
        for op, term in zip(it, it, strict=False):
            if op == "+":
                pool._dice_list.extend(term.result._dice_list)
                modifier += term.modifier
            elif op == "-":
                if len(term.result) > 0:
                    raise ValueError("Subtracting dice pools is not allowed in DnD5 notation")
                modifier -= term.modifier

        return ParsedRoll(pool, modifier)

    @v_args(inline=True)
    def term(self, item: ParsedRoll | Token) -> ParsedRoll:
        """
        Process individual terms (dice expressions or modifiers).

        Args:
        ----
            item: Either a parsed dice expression or integer modifier token

        Returns:
        -------
            ParsedRoll with either dice pool or modifier

        """
        if isinstance(item, ParsedRoll):
            return item
        else:  # int modifier
            return ParsedRoll(DicePool([]), int(item))

    @v_args(inline=True)
    def dice_expr(
        self,
        count: Token | None,
        d_literal: Token,
        sides: Token,
        roll_mod: tuple[str, Token] | None = None,
    ) -> ParsedRoll:
        """
        Process dice expressions like "2d6" or "4d6kh3".

        Args:
        ----
            count: Number of dice to roll (None means 1)
            sides: Number of sides on each die
            d_literal: Number of dice
            roll_mod: Optional roll modifier (e.g., ("keep_highest", "3"))

        Returns:
        -------
            ParsedRoll containing the constructed dice pool and zero modifier

        """
        count_val = 1 if count is None else int(count)
        sides_val = int(sides)
        base_pool = DicePool([create_dice(biggest_side=sides_val) for _ in range(count_val)])

        if roll_mod is None:
            return ParsedRoll(base_pool, 0)

        mod_type, mod_value = roll_mod
        mod_value_int = int(mod_value)
        if mod_type == "keep_highest":
            kept_rolls = kh(base_pool, mod_value_int)
        elif mod_type == "keep_lowest":
            kept_rolls = kl(base_pool, mod_value_int)
        elif mod_type == "drop_highest":
            kept_rolls = dh(base_pool, mod_value_int)
        elif mod_type == "drop_lowest":
            kept_rolls = dl(base_pool, mod_value_int)
        else:
            raise ValueError(f"Unknown roll modifier: {mod_type}")

        new_pool = DicePool([create_dice(biggest_side=sides_val) for _ in kept_rolls])
        return ParsedRoll(new_pool, 0)

    def modifier(self, items: list[Token]) -> int:
        """
        Convert modifier token to integer.

        Args:
        ----
            items: List containing a single integer token

        Returns:
        -------
            Integer value of the modifier

        """
        return int(items[0])

    def keep_highest(self, items: list[Token]) -> tuple[Literal["keep_highest"], Token]:
        """
        Handle 'kh' (keep highest) roll modifier.

        Args:
        ----
            items: List containing the keep count token

        Returns:
        -------
            Tuple indicating modifier type and count

        """
        return ("keep_highest", items[0])

    def keep_lowest(self, items: list[Token]) -> tuple[Literal["keep_lowest"], Token]:
        """
        Handle 'kl' (keep lowest) roll modifier.

        Args:
        ----
            items: List containing the keep count token

        Returns:
        -------
            Tuple indicating modifier type and count

        """
        return ("keep_lowest", items[0])

    def drop_highest(self, items: list[Token]) -> tuple[Literal["drop_highest"], Token]:
        """
        Handle 'dh' (drop highest) roll modifier.

        Args:
        ----
            items: List containing the drop count token

        Returns:
        -------
            Tuple indicating modifier type and count

        """
        return ("drop_highest", items[0])

    def drop_lowest(self, items: list[Token]) -> tuple[Literal["drop_lowest"], Token]:
        """
        Handle 'dl' (drop lowest) roll modifier.

        Args:
        ----
            items: List containing the drop count token

        Returns:
        -------
            Tuple indicating modifier type and count

        """
        return ("drop_lowest", items[0])


# Global LALR parser instance with built-in transformer
_PARSER = Lark.open(
    "dice_grammar.lark",
    rel_to=__file__,
    parser="lalr",
    transformer=DiceTransformer(),
)


def parse_dice_notation(notation: str) -> ParsedRoll:
    """
    Parse DnD5-style dice notation into structured roll objects.

    Supports standard DnD5 notation patterns including:
        - "d20"         → Single d20 die
        - "2d6+3"       → Two d6 dice with +3 modifier
        - "4d6kh3"      → Four d6 dice, keep 3 highest
        - "2d20dl1"     → Two d20 dice, drop 1 lowest

    Args:
    ----
        notation: DnD5 dice notation string (e.g., "2d6+1")

    Returns:
    -------
        ParsedRoll: Structured result containing dice pool and modifier

    Raises:
    ------
        ValueError: For invalid notation (e.g., subtracting dice pools)
        lark.exceptions.LarkError: For syntax errors in notation

    Examples:
    --------
        >>> parse_dice_notation("2d6+3")
        ParsedRoll(result=DicePool([...]), modifier=3)
        >>> parse_dice_notation("4d6kh3")
        ParsedRoll(result=DicePool([...]), modifier=0)

    """
    tree: Tree[Token] = _PARSER.parse(notation)
    transformer = DiceTransformer()
    return transformer.transform(tree)
