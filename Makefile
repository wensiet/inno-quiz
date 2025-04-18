run:
	poetry run uvicorn src.main:create_app --host 0.0.0.0 --port 8000 --reload --factory

test:
	poetry run pytest

lint:
	poetry run ruff check src tests alembic --fix
	poetry run ruff format src tests alembic
	poetry run mypy src tests --show-error-codes
	poetry run toml-sort pyproject.toml --in-place --all
