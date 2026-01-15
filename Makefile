.PHONY: install project build publish package-install lint

install:
	poetry install

project:
	poetry run project

build:
	poetry build

publish:
	poetry publish --dry-run

package-install:
	python3 -m pip install dist/*.whl

lint:
	poetry run ruff check .

test:
	poetry run pytest tests/ -v

clean:
	rm -rf dist build
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

format:
	poetry run ruff format .