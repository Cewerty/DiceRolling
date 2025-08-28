PROJECT_NAME = diceroller
SRC_DIR = src
TESTS_DIR = tests

.PHONY: all install-hooks lint format typecheck test build clean ci

all: install-hooks lint format typecheck test build

install-hooks:
	@echo "Установка pre-commit хуков..."
	pre-commit install

lint:
	@echo "🔍 Запуск линтинга..."
	ruff check $(SRC_DIR) $(TESTS_DIR)

format:
	@echo "🎨 Форматирование кода..."
	ruff format $(SRC_DIR) $(TESTS_DIR)

typecheck:
	@echo "🧪 Проверка типов..."
	mypy $(SRC_DIR)
	PYTHONPATH=$(SRC_DIR) mypy $(TESTS_DIR)

test:
	@echo "🚀 Запуск тестов..."
	pytest $(TESTS_DIR) -v --cov=$(SRC_DIR) --cov-report=term-missing

build:
	@echo "📦 Сборка пакета..."
	uv build --no-build-isolation

clean:
	@echo "🧹 Очистка артефактов..."
	rm -rf build dist .mypy_cache .pytest_cache .coverage .ruff_cache

ci: lint typecheck test build