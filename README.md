# DiceRolling — Python-библиотека для симуляции кубиков настольных RPG

[![CI Pipeline](https://github.com/Cewerty/DiceRolling/actions/workflows/ci.yaml/badge.svg)](https://github.com/your-username/diceroller/actions)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

`diceroller` — это типизированная, расширяемая и тестируемая python библиотека для работы с кубиками настольных ролевых игр (TRPG), таких как **Dungeons & Dragons**, **Pathfinder** и другие. Она предоставляет гибкую модель кубиков (`Dice`) и пулов (`DicePool`), поддержку продвинутых механик (преимущество/помеха, keep/drop), стратегии бросков и готова к интеграции в **REST API** (FastAPI) или **Discord-боты**.

---

## 🔥 Возможности

- **Иммутабельные кубики** (`Dice`) и **мутируемые пулы** (`DicePool`)
- Поддержка всех стандартных кубиков: `d4`, `d6`, `d8`, `d10`, `d12`, `d20`, `d100`
- Продвинутые механики:
  - `adv()` / `dis()` — преимущество и помеха
  - `kh()` / `kl()` — оставить лучшие/худшие броски
  - `dh()` / `dl()` — отбросить лучшие/худшие броски
- **Стратегии бросков** (GoF Strategy):
  - Стандартный, с преимуществом, с помехой, множественный бросок
- **Контекстные менеджеры** для временной подмены стратегий
- **Сериализация в/из `dict`** — идеально для FastAPI и Pydantic
- Поддержка **вложенных списков** и **гибкого ввода**
- Полная **типовая безопасность** (`mypy --strict`)
- Чистая архитектура: **протоколы**, **фабрики**, **алиасы**

---

## 🚀 Быстрый старт

### Установка

```bash
pip install diceroller
```

### Примеры использования

```python
from diceroller import d6, d20, DicePool
from diceroller import adv, kh, throws

# Создание кубиков
d20_roll = d20().roll()          # 1–20
d6_plus_2 = d6() + 2             # Бросок d6 с модификатором +2

# Преимущество (бросить 2 раза, взять максимум)
attack_with_adv = adv(d20())     # Эквивалент 2d20kh1

# Пул кубиков и keep highest
stats = DicePool([d6(), d6(), d6(), d6()])
best_three = kh(stats, 3)        # 4d6kh3 — классическая генерация характеристик

# Генерация серии бросков
for roll in throws(d6(), count=5):
    print(roll)  # → 3, 5, 1, 6, 2

# Сериализация для API
pool = DicePool([d6(), d8()])
api_data = pool.to_dict()
# {'dice': [{'smallest_side': 1, 'biggest_side': 6}, {'smallest_side': 1, 'biggest_side': 8}]}
```

---

## Архитектурные особенности 🧩

### Гибкость через стратегии

```python
from diceroller.strategies import AdvantageRoll, PseudoRandomStrategy

# Временно заменить стратегию броска
with DiceContext(d20(), replaced_roll_strategy=AdvantageRoll()) as lucky_d20:
    result = lucky_d20.roll()  # Автоматически с преимуществом!
```

### Расширяемость

- Создавайте свои стратегии рандомизации (например, на основе numpy)
- Реализуйте кастомные механики бросков
- Интегрируйте с вашими TRPG-системами

### Готовность к продакшену

- ✅ Покрытие тестами (pytest + coverage)
- ✅ CI/CD (GitHub Actions)
- ✅ Pre-commit хуки (ruff, mypy)
- ✅ Документация (Sphinx)
- ✅ Поддержка py.typed

---

## Структура проекта

```plain-text
src/
├── diceroller/
│   ├── dice.py              # Ядро: Dice, DicePool
│   ├── strategies/          # Стратегии бросков и рандомизации
│   ├── aliases/             # Удобные алиасы (d6, d20)
│   ├── factories/           # Фабрики кубиков
│   └── utils/
│       └── context_managers/ # Контекстные менеджеры
tests/                       # pytest тесты
docs/                        # Документация Sphinx
```

---

## Лицензия

MIT — свободно используйте в личных и коммерческих проектах.
