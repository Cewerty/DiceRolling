"""Base module for dice roller context managers."""

from abc import ABC, abstractmethod
from contextlib import AbstractContextManager
from types import TracebackType
from typing import Literal

from ...dice import Dice
from ...strategies import DefaultRandomStrategy, DefaultRoll, RandomStrategy, RollStrategy


class BaseDiceContextManager(AbstractContextManager, ABC):
    """Base context manager for dice operations with strategy replacement."""

    def __init__(
        self,
        initial_dice: Dice,
        replaced_rng_strategy: RandomStrategy | None = None,
        replaced_roll_strategy: RollStrategy | None = None,
    ) -> None:
        """
        Initialize the context manager with dice and optional strategies.

        Args:
        ----
            initial_dice: The original dice instance to proxy
            replaced_rng_strategy: Optional RNG strategy to temporarily use
            replaced_roll_strategy: Optional roll strategy to temporarily use

        """
        self.initial_dice = initial_dice
        self.temp_rng_strategy = replaced_rng_strategy if replaced_rng_strategy is not None else DefaultRandomStrategy()
        self.temp_roll_strategy = replaced_roll_strategy if replaced_roll_strategy is not None else DefaultRoll()
        self.proxy_dice: Dice | None = None

    def __enter__(self) -> Dice:
        """
        Enter the context and create a proxy dice with temporary strategies.

        Returns
        -------
            A proxy dice instance with the temporary strategies applied

        """
        self.proxy_dice = Dice(
            self.initial_dice.smallest_side,
            self.initial_dice.biggest_side,
            self.temp_rng_strategy,
            self.temp_roll_strategy,
        )
        self.on_enter()
        return self.proxy_dice

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        """
        Exit the context and clean up the proxy dice.

        Args:
        ----
            exc_type: Exception type if an exception was raised
            exc_value: Exception value if an exception was raised
            traceback: Traceback if an exception was raised

        Returns:
        -------
            False to not suppress any exceptions

        """
        self.on_exit(exc_type, exc_value, traceback)
        self.proxy_dice = None
        return False

    @abstractmethod
    def on_enter(self) -> None:
        """Abstract method called when entering the context."""
        pass

    @abstractmethod
    def on_exit(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """
        Abstract method called when exiting the context.

        Args:
        ----
            exc_type: Exception type if an exception was raised
            exc_value: Exception value if an exception was raised
            traceback: Traceback if an exception was raised

        """
        pass


class DiceContext(BaseDiceContextManager):
    """Simple dice context manager with no additional behavior."""

    def on_enter(self) -> None:
        """No-op implementation for context entry."""
        pass

    def on_exit(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """
        No-op implementation for context exit.

        Args:
        ----
            exc_type: Exception type if an exception was raised
            exc_value: Exception value if an exception was raised
            traceback: Traceback if an exception was raised

        """
        pass
