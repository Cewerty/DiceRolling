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

from __future__ import annotations

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

    Methods
    -------
        process_start: Process the start rule of the grammar
        process_expr: Process expressions with operators (+ and -)
        process_term: Process a single term (dice expression or number)
        process_dice_expr: Process dice expressions with optional roll modifiers

    """

    def process_start(self, expr: ParsedRoll) -> ParsedRoll:
        """
        Process the start rule of the grammar.

        Args:
        ----
            expr: The parsed expression from the grammar

        Returns:
        -------
            ParsedRoll: The same expression, passed through unchanged

        Example:
        -------
            >>> engine = DiceTransformationEngine()
            >>> roll = ParsedRoll(DicePool([]), 0)
            >>> result = engine.process_start(roll)
            >>> result is roll
            True

        """
        return expr

    def process_expr(self, items: list) -> ParsedRoll:
        """
        Process expressions with operators (+ and -).

        Combines multiple dice pools and modifiers based on operators.
        Addition merges dice pools and adds modifiers. Subtraction is only
        allowed for numeric modifiers, not dice pools.

        Args:
        ----
            items: List of terms and operators [term1, op1, term2, op2, term3, ...]

        Returns:
        -------
            ParsedRoll: Combined result with merged pools and modifiers

        Raises:
        ------
            ValueError: If attempting to subtract a dice pool (only modifiers allowed)

        Example:
        -------
            >>> engine = DiceTransformationEngine()
            >>> term1 = ParsedRoll(DicePool([d6()]), 2)
            >>> term2 = ParsedRoll(DicePool([]), 3)
            >>> result = engine.process_expr([term1, "+", term2])
            >>> result.modifier
            5

        """
        if not items:
            return ParsedRoll(DicePool([]), 0)

        current = items[0]
        if not isinstance(current, ParsedRoll):
            current = ParsedRoll(DicePool([]), 0)

        i = 1
        while i < len(items):
            if i + 1 >= len(items):
                break

            op = items[i]
            next_term = items[i + 1]

            if not isinstance(next_term, ParsedRoll):
                next_term = ParsedRoll(DicePool([]), 0)

            operator = str(op) if isinstance(op, (str | Token)) else op

            if operator in {"+", "add"}:
                if isinstance(current.result, DicePool) and isinstance(next_term.result, DicePool):
                    new_pool = DicePool(current.result._dice_list + next_term.result._dice_list)
                    current = ParsedRoll(new_pool, current.modifier + next_term.modifier)
                else:
                    current = ParsedRoll(current.result, current.modifier + next_term.modifier)
            elif operator in {"-", "sub"}:
                if isinstance(next_term.result, DicePool) and len(next_term.result._dice_list) > 0:
                    raise ValueError("Subtracting dice pools is not allowed")
                current = ParsedRoll(current.result, current.modifier - next_term.modifier)

            i += 2

        return current

    def process_term(self, item: ParsedRoll | Token) -> ParsedRoll:
        """
        Process a single term (either dice expression or number).

        Args:
        ----
            item: Either a ParsedRoll (from dice_expr)
                or a Token representing a numeric literal

        Returns:
        -------
            ParsedRoll: Wrapped term as ParsedRoll. Numbers become modifiers
                with empty pools

        Example:
        -------
            >>> engine = DiceTransformationEngine()
            >>> token = Token("INT", "5")
            >>> result = engine.process_term(token)
            >>> result.modifier
            5
            >>> result.result
            DicePool([])

        """
        if isinstance(item, ParsedRoll):
            return item
        if isinstance(item, Token) and item.type == "INT":
            return ParsedRoll(DicePool([]), int(item))
        return ParsedRoll(DicePool([]), 0)

    @staticmethod
    def _process_count(count: Any) -> int:  # noqa: ANN401
        """
        Process and normalize dice count from various input types.

        Handles conversion of count parameter from Lark tokens, trees,
        or primitive types to a standardized integer value.

        Args:
        ----
            count: Input count value. Can be:
                - None: defaults to 1
                - Token(INT): integer token from parser
                - str: digit string
                - int: direct integer value
                - Tree: parse tree with count data

        Returns:
        -------
            int: Normalized dice count (defaults to 1 if invalid)

        Example:
        -------
            >>> DiceTransformationEngine._process_count(Token("INT", "3"))
            3
            >>> DiceTransformationEngine._process_count(None)
            1
            >>> DiceTransformationEngine._process_count("5")
            5

        Note:
        ----
            This is an internal utility method for normalizing parser output

        """
        if count is None:
            return 1
        if (isinstance(count, Token) and count.type == "INT") or (isinstance(count, str) and count.isdigit()):
            return int(count)
        elif isinstance(count, int):
            return count
        elif isinstance(count, Tree) and count.data == "count" and count.children:
            child = count.children[0]
            if isinstance(child, Token) and child.type == "INT":
                return int(child)
        return 1

    @staticmethod
    def _process_sides(sides: Any) -> int:  # noqa: ANN401
        """
        Process and normalize dice sides from various input types.

        Handles conversion of sides parameter from Lark tokens, trees,
        or primitive types to a standardized integer value.

        Args:
        ----
            sides: Input sides value. Can be:
                - None: defaults to 6
                - Token(INT): integer token from parser
                - str: digit string
                - int: direct integer value
                - Tree: parse tree with sides data

        Returns:
        -------
            int: Normalized dice sides (defaults to 6 if invalid)

        Example:
        -------
            >>> DiceTransformationEngine._process_sides(Token("INT", "20"))
            20
            >>> DiceTransformationEngine._process_sides(None)
            6
            >>> DiceTransformationEngine._process_sides("8")
            8

        Note:
        ----
            This is an internal utility method for normalizing parser output

        """
        if sides is None:
            return 6
        if isinstance(sides, Token) and sides.type == "INT":  # noqa: SIM114
            return int(sides)
        elif isinstance(sides, str) and sides.isdigit():
            return int(sides)
        elif isinstance(sides, int):
            return sides
        elif isinstance(sides, Tree) and hasattr(sides, "data") and sides.data == "sides" and sides.children:
            child = sides.children[0]
            if isinstance(child, Token) and child.type == "INT":
                return int(child)
        return 6

    @staticmethod
    def _process_mods(base_pool: DicePool | list[int], roll_mods: list[Any] | None) -> DicePool | list[int]:
        """
        Apply roll modifiers to a dice pool using functional composition.

        Processes modifiers like keep_highest, drop_lowest, etc. in sequence,
        creating a new DicePool instance for each transformation. This maintains
        immutability and enables easy debugging of the transformation chain.

        Args:
        ----
            base_pool: Initial dice pool before modifiers
            roll_mods: List of modifier specifications. Each can be:
                - Tree node from Lark parse tree
                - Tuple (modifier_type, value)
                - None (ignored)

        Returns:
        -------
            DicePool: New pool with all modifiers applied sequentially

        Raises:
        ------
            ValueError: If unknown modifier type encountered
            DiceInvalidAmountError: If modifier value is invalid (e.g., keep 0 dice)

        Example:
        -------
            >>> base = DicePool([d6(), d6(), d6(), d6()])
            >>> modified = _process_mods(base, [("keep_highest", 3)])
            # Returns pool with 3 dice (highest kept from 4d6)

        Note:
        ----
            - Modifiers are applied in order of appearance
            - Each modifier creates a new pool instance (immutability)
            - Empty modifier lists return the base pool unchanged

        """
        if not roll_mods:
            return base_pool

        result_pool = base_pool
        modifier_map = {
            "keep_highest": kh,
            "keep_lowest": kl,
            "drop_highest": dh,
            "drop_lowest": dl,
        }

        for mod in roll_mods:
            if not mod:
                continue
            if isinstance(mod, Tree):
                mod_type = mod.data
                mod_value = 1
                if mod.children:
                    child = mod.children[0]
                    if isinstance(child, Token) and child.type == "INT":
                        mod_value = int(child)
                if mod_type in modifier_map:
                    result_pool = modifier_map[mod_type](result_pool, mod_value)  # type: ignore[arg-type]
            elif isinstance(mod, tuple):
                mod_type, mod_value = mod
                if mod_type in modifier_map:
                    result_pool = modifier_map[mod_type](result_pool, mod_value)  # type: ignore[arg-type]
        return result_pool

    def process_dice_expr(
        self,
        count: Token | int | str | None = None,
        sides: Token | int | str | None = None,
        roll_mods: list | None = None,
    ) -> ParsedRoll:
        """
        Process dice expressions with optional roll modifiers.

        Transforms notation like "4d6kh3" into a DicePool with
        appropriate keep/drop modifiers applied.

        Args:
        ----
            count: Number of dice to roll. Defaults to 1 if None
            sides: Number of sides on each die
            roll_mods: List of roll modifiers (keep/drop operations)

        Returns:
        -------
            ParsedRoll: DicePool with modifiers applied and zero modifier value

        Raises:
        ------
            ValueError: If number of sides is not positive

        Example:
        -------
            >>> engine = DiceTransformationEngine()
            >>> result = engine.process_dice_expr(2, 6, [("keep_highest", 1)])
            >>> len(result.result)
            1

        """
        count_val = self._process_count(count)
        sides_val = self._process_sides(sides)

        if sides_val <= 0:
            raise ValueError(f"Number of sides must be positive, got {sides_val}")
        base_pool = DicePool([create_dice(biggest_side=sides_val) for _ in range(count_val)])
        result_pool = self._process_mods(base_pool, roll_mods)
        return ParsedRoll(result_pool, 0)


class DiceTransformer(Transformer[Token, ParsedRoll]):
    """
    Lark transformer using composition for transformation logic.

    This class implements the Lark Transformer interface to convert
    parsed syntax trees into structured ParsedRoll objects.

    Attributes
    ----------
        engine: DiceTransformationEngine instance for business logic

    Methods
    -------
        start: Transform the start rule
        expr: Transform expressions with operators
        term: Transform a single term
        dice_expr: Transform dice expressions
        modifier: Process numeric modifiers
        add: Handle '+' operator
        sub: Handle '-' operator
        keep_highest: Handle 'keep highest' modifier
        keep_lowest: Handle 'keep lowest' modifier
        drop_highest: Handle 'drop highest' modifier
        drop_lowest: Handle 'drop lowest' modifier

    """

    def __init__(self) -> None:
        """Initialize the transformer and its engine."""
        super().__init__()
        self.engine = DiceTransformationEngine()

    def start(self, items: list) -> ParsedRoll:
        """
        Transform the start rule of the grammar.

        Args:
        ----
            items: List of parsed items from start rule

        Returns:
        -------
            ParsedRoll: The final parsed roll result

        Example:
        -------
            >>> transformer = DiceTransformer()
            >>> result = transformer.start([ParsedRoll(DicePool([]), 5)])
            >>> result.modifier
            5

        """
        return self.engine.process_start(items[0] if items else ParsedRoll(DicePool([]), 0))

    def expr(self, items: list) -> ParsedRoll:
        """
        Transform expressions with operators.

        Args:
        ----
            items: List of parsed expression components

        Returns:
        -------
            ParsedRoll: Combined expression result

        Example:
        -------
            >>> transformer = DiceTransformer()
            >>> items = [ParsedRoll(DicePool([]), 2), "+", ParsedRoll(DicePool([]), 3)]
            >>> result = transformer.expr(items)
            >>> result.modifier
            5

        """
        return self.engine.process_expr(items)

    def term(self, items: list) -> ParsedRoll:
        """
        Transform a single term.

        Args:
        ----
            items: List containing a single term to process

        Returns:
        -------
            ParsedRoll: Processed term as ParsedRoll

        Example:
        -------
            >>> transformer = DiceTransformer()
            >>> token = Token("INT", "7")
            >>> result = transformer.term([token])
            >>> result.modifier
            7

        """
        return self.engine.process_term(items[0] if items else ParsedRoll(DicePool([]), 0))

    def dice_expr(self, items: list) -> ParsedRoll:
        """
        Transform dice expressions with proper argument handling.

        Handles various dice notation formats including count, sides,
        and roll modifiers.

        Args:
        ----
            items: List of parsed items from the grammar rule.
                For "3d6": [Token(INT, '3'), Token(INT, '6')]
                For "d6": [Token(INT, '6')]
                For "3d6kh3": [Token(INT, '3'), Token(INT, '6'), Tree(keep_highest, [Token(INT, '3')])]

        Returns:
        -------
            ParsedRoll: Processed dice expression

        Example:
        -------
            >>> transformer = DiceTransformer()
            >>> items = [Token("INT", "2"), Token("INT", "6")]
            >>> result = transformer.dice_expr(items)
            >>> len(result.result)
            2

        """
        count = None
        sides = None
        roll_mods = []

        # Отладочная информация для понимания структуры
        # print(f"dice_expr items: {[(type(item), str(item)) for item in items]}")

        if len(items) == 1:
            sides = items[0]
        elif len(items) == 2:  # noqa: PLR2004
            count = items[0]
            sides = items[1]
        else:
            count = items[0]
            sides = items[1]
            roll_mods = items[2:]

        return self.engine.process_dice_expr(count, sides, roll_mods)

    def modifier(self, items: list) -> ParsedRoll:
        """
        Process numeric modifiers.

        Args:
        ----
            items: List containing modifier tokens

        Returns:
        -------
            ParsedRoll: ParsedRoll with numeric modifier and empty pool

        Example:
        -------
            >>> transformer = DiceTransformer()
            >>> items = [Token("INT", "5")]
            >>> result = transformer.modifier(items)
            >>> result.modifier
            5

        """
        if not items:
            return ParsedRoll(DicePool([]), 0)

        token = items[0]
        if isinstance(token, Token) and token.type == "INT":
            return ParsedRoll(DicePool([]), int(token))

        return ParsedRoll(DicePool([]), 0)

    @v_args(inline=True)
    def add(self) -> str:
        """
        Handle '+' operator.

        Returns:
        -------
            str: String representation of addition operator

        Example:
        -------
            >>> transformer = DiceTransformer()
            >>> transformer.add()
            '+'

        """
        return "+"

    @v_args(inline=True)
    def sub(self) -> str:
        """
        Handle '-' operator.

        Returns:
        -------
            str: String representation of subtraction operator

        Example:
        -------
            >>> transformer = DiceTransformer()
            >>> transformer.sub()
            '-'

        """
        return "-"

    @v_args(inline=True)
    def keep_highest(self, value: Token) -> tuple[str, int]:
        """
        Handle 'keep highest' modifier.

        Args:
        ----
            value: Token containing the number of dice to keep

        Returns:
        -------
            tuple[str, int]: Tuple of modifier type and count

        Example:
        -------
            >>> transformer = DiceTransformer()
            >>> token = Token("INT", "3")
            >>> result = transformer.keep_highest(token)
            >>> result
            ('keep_highest', 3)

        """
        return ("keep_highest", int(value))

    @v_args(inline=True)
    def keep_lowest(self, value: Token) -> tuple[str, int]:
        """
        Handle 'keep lowest' modifier.

        Args:
        ----
            value: Token containing the number of dice to keep

        Returns:
        -------
            tuple[str, int]: Tuple of modifier type and count

        Example:
        -------
            >>> transformer = DiceTransformer()
            >>> token = Token("INT", "2")
            >>> result = transformer.keep_lowest(token)
            >>> result
            ('keep_lowest', 2)

        """
        return ("keep_lowest", int(value))

    @v_args(inline=True)
    def drop_highest(self, value: Token) -> tuple[str, int]:
        """
        Handle 'drop highest' modifier.

        Args:
        ----
            value: Token containing the number of dice to drop

        Returns:
        -------
            tuple[str, int]: Tuple of modifier type and count

        Example:
        -------
            >>> transformer = DiceTransformer()
            >>> token = Token("INT", "1")
            >>> result = transformer.drop_highest(token)
            >>> result
            ('drop_highest', 1)

        """
        return ("drop_highest", int(value))

    @v_args(inline=True)
    def drop_lowest(self, value: Token) -> tuple[str, int]:
        """
        Handle 'drop lowest' modifier.

        Args:
        ----
            value: Token containing the number of dice to drop

        Returns:
        -------
            tuple[str, int]: Tuple of modifier type and count

        Example:
        -------
            >>> transformer = DiceTransformer()
            >>> token = Token("INT", "1")
            >>> result = transformer.drop_lowest(token)
            >>> result
            ('drop_lowest', 1)

        """
        return ("drop_lowest", int(value))


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
