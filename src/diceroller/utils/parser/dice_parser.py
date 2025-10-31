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
    version: Module version string (inherited from parent package)

"""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from lark import Lark, Token, Transformer, Tree, v_args

from ...aliases import create_dice
from ...dice import DicePool, dh, dl, kh, kl

if TYPE_CHECKING:
    pass


@dataclass(frozen=True, slots=True)
class ParsedRoll:
    """
    Result of parsing a DnD5 dice notation string.

    Attributes
    ----------
        result (DicePool): The parsed dice pool object.
        modifier (int): The numeric modifier to apply to the roll.

    """

    result: DicePool | list[int]
    modifier: int


class DiceTransformationEngine:
    """
    Handles transformation logic for parsed dice expressions.

    This class encapsulates the business logic for transforming parsed
    dice notation into DicePool objects with appropriate modifiers.
    It separates concerns from the Lark Transformer pattern.
    """

    def process_start(self, expr: ParsedRoll) -> ParsedRoll:
        """
        Process the start rule of the grammar.

        Args:
        ----
            expr (ParsedRoll): The parsed expression from the grammar.

        Returns:
        -------
            ParsedRoll: The same expression, passed through unchanged.

        """
        return expr

    def process_expr(self, first_term: ParsedRoll, *args: Any) -> ParsedRoll:  # noqa: ANN401
        """
        Process expressions with operators (+ and -).

        Combines multiple dice pools and modifiers based on operators.
        Addition merges dice pools and adds modifiers. Subtraction is only
        allowed for numeric modifiers, not dice pools.

        Args:
        ----
            first_term (ParsedRoll): The first term in the expression.
            *args (Any): Alternating operators and terms (op1, term1, op2, term2, ...).

        Returns:
        -------
            ParsedRoll: Combined result with merged pools and modifiers.

        Raises:
        ------
            ValueError: If attempting to subtract a dice pool (only modifiers allowed).

        Example:
        -------
            >>> # Represents: 2d6 + 3 - 1
            >>> # args would be ["+", term_3, "-", term_1]

        """
        pool = first_term.result
        modifier = first_term.modifier

        for i in range(0, len(args), 2):
            if i + 1 >= len(args):
                break

            op = args[i]
            term = args[i + 1]

            if op == "+":
                if isinstance(term.result, DicePool):
                    pool._dice_list.extend(term.result._dice_list)  # type: ignore
                modifier += term.modifier
            elif op == "-":
                if isinstance(term.result, DicePool) and len(term.result._dice_list) > 0:
                    raise ValueError("Subtracting dice pools is not allowed")
                modifier -= term.modifier

        return ParsedRoll(pool, modifier)

    def process_term(self, item: ParsedRoll | Token) -> ParsedRoll:
        """
        Process a single term (either dice expression or number).

        Args:
        ----
            item (ParsedRoll | Token): Either a ParsedRoll (from dice_expr)
                or a Token representing a numeric literal.

        Returns:
        -------
            ParsedRoll: Wrapped term as ParsedRoll. Numbers become modifiers
                with empty pools.

        """
        if isinstance(item, ParsedRoll):
            return item
        return ParsedRoll(DicePool([]), int(item))

    def process_dice_expr(
        self,
        count: Token | None,
        sides: Token,
        roll_mods: list | None = None,
    ) -> ParsedRoll:
        """
        Process dice expressions with optional roll modifiers.

        Transforms notation like "4d6kh3" into a DicePool with
        appropriate keep/drop modifiers applied.

        Args:
        ----
            count (Token | None): Number of dice to roll. Defaults to 1 if None.
            sides (Token): Number of sides on each die.
            roll_mods (list | None, optinal): Tuple of (modifier_type, count)
                where modifier_type is one of: "keep_highest", "keep_lowest",
                "drop_highest", "drop_lowest". Defaults to None.

        Returns:
        -------
            ParsedRoll: DicePool with modifiers applied and zero modifier value.

        Raises:
        ------
            ValueError: If modifier type is not recognized.

        Example:
        -------
            >>> # Input: count=4, sides=6, roll_mod=("keep_highest", "3")
            >>> # Output: ParsedRoll(DicePool([d6, d6, d6, d6]) modified by kh(3))

        """
        count_val = 1 if count is None else int(count)
        sides_val = int(sides)

        base_pool = DicePool([create_dice(biggest_side=sides_val) for _ in range(count_val)])

        if not roll_mods:
            return ParsedRoll(base_pool, 0)

        modifier_map = {
            "keep_highest": kh,
            "keep_lowest": kl,
            "drop_highest": dh,
            "drop_lowest": dl,
        }

        result_pool: DicePool | list[int] = base_pool
        for mod in roll_mods:
            if isinstance(mod, Tree):
                mod_type = mod.data
                mod_value = int(mod.children[0])  # type: ignore
            else:
                mod_type, mod_value = mod

            if mod_type not in modifier_map:
                raise ValueError(f"Unknown roll modifier: {mod_type}")

            result_pool = modifier_map[mod_type](result_pool, mod_value)  # type: ignore

        return ParsedRoll(result_pool, 0)


class DiceTransformer(Transformer[Token, ParsedRoll]):
    """Lark transformer using composition for transformation logic."""

    def __init__(self) -> None:
        """Initialize the transformer and its engine."""
        super().__init__()
        self.engine = DiceTransformationEngine()

    @v_args(inline=True)
    def start(self, expr: ParsedRoll) -> ParsedRoll:
        """Transform the start rule."""
        return self.engine.process_start(expr)

    @v_args(inline=True)
    def expr(self, first_term: ParsedRoll, *args: Any) -> ParsedRoll:  # noqa: ANN401
        """Transform expressions with operators."""
        return self.engine.process_expr(first_term, *args)

    @v_args(inline=True)
    def term(self, item: ParsedRoll | Token) -> ParsedRoll:
        """Transform a single term."""
        return self.engine.process_term(item)

    def dice_expr(self, args: Any) -> ParsedRoll:  # noqa: ANN401
        """
        Transform dice expressions WITHOUT inline=True.

        Handles variable argument count including optional count parameter.
        """
        count = None
        sides = None
        roll_mods = []

        idx = 0

        if isinstance(args[0], Token) and idx < len(args):
            if len(args) > 1:
                count = args[0]
                idx = 1
            else:
                sides = args[0]
                idx = 1

        if idx < len(args):
            sides = args[idx]
            idx += 1

        roll_mods = args[idx:]

        return self.engine.process_dice_expr(count, sides, roll_mods)  # type: ignore


_PARSER = Lark.open(
    "dice_grammar.lark",
    rel_to=__file__,
    parser="lalr",
)


def parse_dice_notation(notation: str) -> ParsedRoll:
    """
    Parse DnD5-style dice notation into structured roll objects.

    Converts human-readable dice notation strings into DicePool objects
    compatible with the diceroller library. Supports standard DnD5 syntax
    including dice rolls, modifiers, and roll modifications.

    Args:
    ----
        notation (str): Dice notation string to parse. Examples:
            - "2d6" - Roll 2 six-sided dice
            - "2d6+3" - Roll 2 six-sided dice and add 3
            - "4d6kh3" - Roll 4 six-sided dice, keep highest 3
            - "2d20-d8+5" - Complex expression (modifiers must be after dice)

    Returns:
    -------
        ParsedRoll: Object containing:
            - result: DicePool object ready for rolling
            - modifier: Numeric modifier to apply to the final roll

    Raises:
    ------
        ValueError: If notation violates DnD5 grammar or contains
            unsupported operations (e.g., "2d6 - d4").
        lark.LarkError: If notation is syntactically invalid.

    Example:
    -------
        >>> result = parse_dice_notation("2d6+3")
        >>> isinstance(result, ParsedRoll)
        True
        >>> result.modifier
        3

    """
    tree: Tree[Token] = _PARSER.parse(notation)
    transformer: DiceTransformer = DiceTransformer()
    return transformer.transform(tree)
