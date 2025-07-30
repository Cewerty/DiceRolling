"""
Модуль содержащий логику, относящуюся к дайсам.

Contains:
- Класс дайсов (Dice)

Пример использования:
>>> dice = Dice(1, 20)
>>> dice.roll()
15
>>> dice.check_success(10)
true

"""

from dataclasses import dataclass, field
from typing import Final

from .dice_strategies import (
    DefaultRandomStrategy,
    DefaultRoll,
    RandomStrategy,
    RollStrategy,
)


@dataclass(slots=True, frozen=True)
class Dice:
    """
    Класс для неизменяемых дайсов.

    Attributes:
        _smallest_side (int): Наименьшая стороны дайса
        _biggest_side (int):  Наибольшая стороны дайса
        _randomization_strategy (RandomStrategy): Стратегия генерации случайных чисел
        _roll_strategy (RollStrategy): Стратегия броска дайса

    Raises:
        ValueError: При ситуации, когда наименьшая сторона больше наибольшей или меньше нуля

    """

    _smallest_side: Final[int]
    _biggest_side: Final[int]
    _randomization_strategy: Final[RandomStrategy] = field(default_factory=DefaultRandomStrategy)
    _roll_strategy: Final[RollStrategy] = field(default_factory=DefaultRoll)

    def __post_init__(self) -> None:
        """
        Инициализирует проверку на корректность сторон дайса.

        Raises:
            ValueError: возвращается в тех случах, когда наименьшая сторона больше наибольшей или меньше нуля

        """
        if self.smallest_side >= self.biggest_side or self.smallest_side < 0:
            raise ValueError(
                f"Incorrect sides: smallest_side ({self._smallest_side}) must be non-negative"
                f"and less than biggest_side ({self._biggest_side})."
            )

    @property
    def smallest_side(self) -> int:
        """
        Возвращает наименьшую сторону дайса.

        Returns:
            int: Наименьшая сторона дайса (только для чтения)

        Note:
            Значение устанавливается при создании экземпляра

        """
        return self._smallest_side

    @property
    def biggest_side(self) -> int:
        """
        Возвращает наибольшую сторону дайса.

        Returns:
            int: Наибольшая стороная дайса (только для чтения)

        Note:
            Значение устанавливается при создании экземпляра

        """
        return self._biggest_side

    @property
    def randomization_strategy(self) -> RandomStrategy:
        """
        Возвращает стратегию генерации случайных чисел.

        Returns:
            RandomStrategy: Стратегия генерации случайных чисел

        Note:
            Значение устанавливается при создании экземпляра

        """
        return self._randomization_strategy

    @property
    def roll_strategy(self) -> RollStrategy:
        """
        Возвращает стратегию броска дайса.

        Returns:
            RollStrategy: стратегия броска дайса

        """
        return self._roll_strategy

    def check_success(self, check: int, inserted_roll_strategy: RollStrategy | None = None) -> bool:
        """
        Проверяет успешность проходения проверки при броске кубика.

        Args:
            check (int): значение проверки
            inserted_roll_strategy (RollStrategy | None, optional): стратегия для броска

        Returns:
            bool: прохождение или провал проверки

        """
        return self.roll(inserted_roll_strategy=inserted_roll_strategy) >= check

    def roll(
        self,
        modifier: int = 0,
        inserted_roll_strategy: RollStrategy | None = None,
    ) -> int:
        """
        Выполняет бросок дайса с заданным модификатором.

        Args:
            inserted_roll_strategy (RollStrategy | None, optional): стратегия для броска. Defaults to None.
            modifier (int, optional): модификатор броска. Defaults to 0.

        Returns:
            int: значение броска

        """
        if inserted_roll_strategy is None:
            return self.roll_strategy.roll(self, modifier)
        return inserted_roll_strategy.roll(self, modifier)
