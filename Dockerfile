FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VENV="/opt/poetry-venv" \
    POETRY_CACHE_DIR="/opt/.cache"

# Install Poetry
RUN apt-get update && apt-get install -y curl \
    && curl -sSL https://install.python-poetry.org | python3 - -- --path $POETRY_HOME \
    && apt-get purge -y --auto-remove curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Add Poetry to PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Copy configuration files
COPY pyproject.toml poetry.lock* ./

# Configure Poetry to not create a virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-dev

# Copy project files
COPY . .

# Expose ports
EXPOSE 8000 8501

# Default command
CMD ["uvicorn", "src.main:create_app", "--host", "0.0.0.0", "--port", "8000", "--factory"] 