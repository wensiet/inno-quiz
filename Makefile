run:
	poetry run uvicorn src.main:create_app --host 0.0.0.0 --port 8000 --reload --factory & \
	poetry run streamlit run src/streamlit/app.py & \
	wait

backend:
	poetry run uvicorn src.main:create_app --host 0.0.0.0 --port 8000 --reload --factory

frontend:
	poetry run python src/streamlit/run.py

test:
	poetry run pytest --cov=src --cov-report=term-missing --cov-report=xml

test-verbose:
	poetry run pytest -v --cov=src --cov-report=term-missing --cov-report=xml

lint:
	poetry run ruff check src tests alembic --fix
	poetry run ruff format src tests alembic
	poetry run mypy src tests --show-error-codes
	poetry run toml-sort pyproject.toml --in-place --all

migrate:
	poetry run alembic upgrade head
