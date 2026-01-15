.PHONY: install project build publish package-install lint

install:
	poetry install --no-root  # Только зависимости, без установки проекта

project:
	poetry run python __main__.py  # Запуск напрямую

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