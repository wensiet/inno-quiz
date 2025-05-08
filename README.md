# InnoQuiz

A web application for creating and taking thematic quizzes.

## Features

- **Quiz Creation**: Create custom quizzes with multiple-choice questions
- **Quiz Participation**: Take quizzes and view your results
- **Leaderboard**: See top scores for each quiz
- **External API Integration**: Generate questions from Open Trivia DB

## Tech Stack

- Python 3.12
- FastAPI (Backend REST API)
- SQLite (Database)
- Streamlit (Frontend UI)
- Alembic (Database migrations)

## Setup

1. Clone the repository:

```bash
git clone https://github.com/your-username/inno-quiz.git
cd inno-quiz
```

2. Install Poetry if you don't have it:

```bash
pip install poetry
```

3. Install the dependencies:

```bash
poetry install
```

4. Create a `.env` file:

```bash
cp .env.local .env
```

5. Run database migrations:

```bash
make migrate
```

## Running the Application

### Option 1: Using Make Commands

1. Start the backend API server and the Streamlit frontend:

```bash
make run
```

This will start the FastAPI backend on http://localhost:8000 and start the Streamlit frontend on http://localhost:8501

### Option 2: Using Docker Compose

You can also run the entire stack using Docker Compose:

```bash
docker-compose up -d
```

## API Documentation

Once the server is running, you can view the OpenAPI documentation at:

- http://localhost:8000/docs (Swagger UI)

## Development
-

### Testing

Run the test suite with coverage reporting:

```bash
make test
```

For more verbose test output:

```bash
make test-verbose
```

#### Test coverage

```bash
================================ tests coverage ================================
_______________ coverage: platform linux, python 3.12.10-final-0 _______________

Name                                  Stmts   Miss  Cover   Missing
-------------------------------------------------------------------
src/__init__.py                           0      0   100%
src/api/__init__.py                      10      0   100%
src/api/auth.py                          28      0   100%
src/api/questions.py                     60      5    92%   53, 95, 99, 119, 123
src/api/quiz_results.py                  56      6    89%   47, 50, 72-74, 95
src/api/quizzes.py                       42      4    90%   68, 72, 87, 91
src/api/trivia.py                        49     33    33%   20-32, 49-69, 95-158
src/api/users.py                         42      3    93%   48, 67, 86
src/auth/__init__.py                      3      0   100%
src/auth/dependencies.py                 49      3    94%   56, 96, 107
src/auth/utils.py                        21      0   100%
src/choices.py                            5      0   100%
src/crud/__init__.py                      0      0   100%
src/crud/quiz.py                        117      7    94%   75, 90, 137, 152, 162-164
src/crud/user.py                         49      2    96%   61, 84
src/external/__init__.py                  0      0   100%
src/external/trivia.py                   57     49    14%   35-96, 109-122
src/main.py                              24      0   100%
src/models/__init__.py                    0      0   100%
src/models/base.py                       12      0   100%
src/models/quiz.py                       31      0   100%
src/models/user.py                        9      0   100%
src/schemas/__init__.py                   0      0   100%
src/schemas/quiz.py                      87      0   100%
src/schemas/user.py                      27      0   100%
src/settings/__init__.py                  0      0   100%
src/settings/database.py                 14      1    93%   19
src/settings/general.py                  21      3    86%   33-35
src/utils/__init__.py                     0      0   100%
src/utils/base/__init__.py                0      0   100%
src/utils/base/auth.py                    4      4     0%   1-6
src/utils/base/repository.py             59     59     0%   1-103
src/utils/base/service.py                 4      4     0%   1-6
src/utils/base/settings.py                3      0   100%
src/utils/cache.py                        9      9     0%   1-21
src/utils/dependencies.py                17      6    65%   21-22, 28-31
src/utils/exceptions.py                  38      1    97%   28
src/utils/filters.py                      4      4     0%   1-6
src/utils/logger.py                       0      0   100%
src/utils/orm.py                         36      7    81%   67-74
src/utils/response.py                     7      7     0%   1-12
tests/__init__.py                         0      0   100%
tests/conftest.py                        64      0   100%
tests/test_api.py                        64      0   100%
tests/test_auth.py                       35      0   100%
tests/test_auth_dependencies.py          45      0   100%
tests/test_crud.py                      178      0   100%
tests/test_exceptions.py                 15      0   100%
tests/test_main.py                       43      0   100%
tests/test_questions.py                  67      0   100%
tests/test_questions_coverage.py         37      0   100%
tests/test_quiz_results.py               73      1    99%   127
tests/test_quiz_results_coverage.py      34      0   100%
tests/test_quizzes.py                    69      0   100%
tests/test_schema_validators.py          19      0   100%
tests/test_users.py                      72      0   100%
-------------------------------------------------------------------
TOTAL                                  1809    218    88%
Required test coverage of 60% reached. Total coverage: 87.95%
```
