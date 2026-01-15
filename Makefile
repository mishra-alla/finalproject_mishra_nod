.PHONY: install project build publish package-install lint

install:
	poetry install --no-root

project:
	python3 __main__.py  # ← ИЗМЕНИЛИ python на python3

build:
	@echo "Сборка пакета отключена (простая структура)"

publish:
	@echo "Публикация отключена"

package-install:
	@echo "Установка пакета отключена"

lint:
	poetry run ruff check .

test:
	poetry run pytest tests/ -v

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

format:
	poetry run ruff format .

run: project