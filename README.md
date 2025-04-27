# USPolis Backend

[MongoDB]: https://www.mongodb.com "MongoDB NoSQL homepage"
[FastAPI]: https://fastapi.tiangolo.com "FastAPI web framework"
[Beanie ODM]: https://roman-right.github.io/beanie/ "Beanie object-document mapper"
[Starlette]: https://www.starlette.io "Starlette web framework"
[PyDantic]: https://pydantic-docs.helpmanual.io "PyDantic model validation"
[fastapi-jwt]: https://github.com/k4black/fastapi-jwt "JWT auth for FastAPI"
[fastapi-mail]: https://github.com/sabuhish/fastapi-mail "FastAPI mail server"
[uvicorn]: https://www.uvicorn.org "Uvicorn ASGI web server"
[mypy]: https://www.mypy-lang.org "mypy Python type checker"
[ruff]: https://docs.astral.sh/ruff/ "Ruff code linter and formatter"

## Table of Contents
- [Stack](#stack)
- [Docs](#docs)
- [Setup](#setup)
- [Run](#run)
- [Develop](#develop)
- [Test](#test)

## Stack

- [FastAPI](https://fastapi.tiangolo.com/) - Python async micro framework built on [Starlette](https://www.starlette.io/) and [PyDantic](https://docs.pydantic.dev/latest/).
- [SQL Model](https://sqlmodel.tiangolo.com/) - Python library for interacting with SQL databases, powered by [PyDantic](https://docs.pydantic.dev/latest/) and [SQLAlchemy](https://sqlalchemy.org/).
- [PostgreSQL](https://www.postgresql.org/) - Open source object-relational database. 

## Docs

You can see a complete documentation at [USPolis-Admin Wiki](https://github.com/PCS-Poli-USP/USPolis-Admin/wiki).

## Setup

This codebase was written for Python 3.12 and above. Don't forget about a venv as well, in this project we use [Poetry](https://python-poetry.org/docs/) for dependency management. 

First we'll need to install poetry using [pipx](https://pipx.pypa.io/stable/)

```bash
pipx install poetry
```

After installing poetry now we will install only the core dependencies
```bash
poetry install --without test,dev
```

There are other settings in `config.py` and the included `.env` file, you can see all enviroment variables used at `.env.example` file. 

Assuming you've created and setted the '.env' file, everything should run as-is if there is a local [PostgreSQL](https://www.postgresql.org/) instance running (see the [docs](https://github.com/PCS-Poli-USP/USPolis-Admin/wiki) for a complete step by step to how set the enviroment).

## Run

This sample uses [uvicorn](https://www.uvicorn.org/) as our ASGI web server. This allows us to run our server code in a much more robust and configurable environment than the development server. For example, ASGI servers let you run multiple workers that recycle themselves after a set amount of time or number of requests.

```bash
uvicorn server.main:app --reload --port 8080
```

You're API should now be available at http://localhost:8080

## Develop

This codebase is uses [mypy](https://mypy.readthedocs.io/en/stable/) for type checking and [ruff](https://docs.astral.sh/ruff/) for everything else. 

Install both with the dev tag.

```bash
poetry install --with dev
```

To run the type checker (if you use VSCode you can install [MyPy extension](https://marketplace.visualstudio.com/items/?itemName=matangover.mypy)):

```bash
mypy server
```

To run the linter and code formatter:

```bash
ruff check server
ruff format server
```

## Test

The sample app also comes with a test suite to get you started, we use [Pytest](https://docs.pytest.org/en/stable/) for testing.

Make sure to install the requirements found in the test folder before trying to run the tests.

```bash
poetry install --with test
```

The tests need access to a PostgreSQL database that is emptied at the end of each test. 

Then just run the test suite.

```bash
pytest
```
