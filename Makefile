.PHONY: install project build publish package-install lint

install:
	poetry install

project:
	poetry run project

lint:
	poetry run ruff check .

test:
	poetry run pytest tests/ -v

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf valutatrade.log

format:
	poetry run ruff format .

run: project

init-data:
	@echo "Initializing data files..."
	echo '[]' > data/users.json
	echo '[]' > data/portfolios.json
	echo '{"pairs": {}, "last_refresh": null}' > data/rates.json
	@echo "Data files initialized"

reset-data:
	@echo "Resetting all data..."
	make init-data
	@echo "All data has been reset"

demo:
	@echo "Setting up demo data..."
	make init-data
	@echo "Demo data ready"

logs:
	@echo "=== Последние логи ==="
	tail -20 valutatrade.log 2>/dev/null || echo "Файл логов не найден"

clear-logs:
	@echo "Очистка логов..."
	> valutatrade.log
	@echo "Логи очищены"