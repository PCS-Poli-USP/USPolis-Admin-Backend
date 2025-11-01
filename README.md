# USPolis Backend
[![Static Badge](https://img.shields.io/badge/Python-3.12-03a84e)](https://www.python.org/)
[![Static Badge](https://img.shields.io/badge/FastAPI-0cc2b6)](https://fastapi.tiangolo.com)
[![Static Badge](https://img.shields.io/badge/SQLModel-7c2ea3)](https://sqlmodel.tiangolo.com/)
[![Static Badge](https://img.shields.io/badge/SQLAlchemy-edc309)](https://www.sqlalchemy.org/)
[![Static Badge](https://img.shields.io/badge/PostgreSQL-1965c2)](https://www.postgresql.org/)
[![Static Badge](https://img.shields.io/badge/Pydantic-c22141)](https://docs.pydantic.dev/latest/)
[![Static Badge](https://img.shields.io/badge/mypy-gray)](https://www.mypy-lang.org)
[![Static Badge](https://img.shields.io/badge/Ruff-6c09ed)](https://docs.astral.sh/ruff/)

![USPolis-removebg-preview](https://github.com/user-attachments/assets/c19e3ce9-646c-4404-926c-4115c4a5a0b8)


## Table of Contents
1. [Stack](#stack)
2. [Docs](#docs)
3. [Setup](#setup)
4. [Run](#run)
5. [Develop](#develop)
6. [Test](#test)

## Stack
Here we have the tecnologies used on backend:
- [FastAPI](https://fastapi.tiangolo.com/) - Python async micro framework built on [Starlette](https://www.starlette.io/) and [PyDantic](https://docs.pydantic.dev/latest/).
- [SQL Model](https://sqlmodel.tiangolo.com/) - Python library for interacting with SQL databases, powered by [PyDantic](https://docs.pydantic.dev/latest/) and [SQLAlchemy](https://sqlalchemy.org/).
- [PostgreSQL](https://www.postgresql.org/) - Open source object-relational database. 

## Docs

You can see a complete documentation at [USPolis-Admin Wiki](https://github.com/PCS-Poli-USP/USPolis-Admin/wiki), there you will find our architecture, diagrams, bussiness rules, descriptions and more.

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

There are other settings in `server/config.py` and the included `.env` file, you can see all enviroment variables used at `.env.example` file. 

Assuming you've created and setted the '.env' file, everything should run as-is if there is a local [PostgreSQL](https://www.postgresql.org/) instance running (see the [docs](https://github.com/PCS-Poli-USP/USPolis-Admin/wiki) for a complete step by step to how set the enviroment).

## Run

This sample uses [uvicorn](https://www.uvicorn.org/) as our ASGI web server. This allows us to run our server code in a much more robust and configurable environment than the development server. For example, ASGI servers let you run multiple workers that recycle themselves after a set amount of time or number of requests.

```bash
uvicorn server.main:app --reload --port 8080
```

Your API should now be available at http://localhost:8080

## Develop

This codebase uses [mypy](https://mypy.readthedocs.io/en/stable/) for type checking and [ruff](https://docs.astral.sh/ruff/) for litting and formatting. 

Install both with the dev tag:

```bash
poetry install --with dev
```
*This is also install some type libraries from other dependencies for mypy

First make sure that .venv is active (you can use [poetry shell](https://github.com/python-poetry/poetry-plugin-shell)): 
```bash
  source .venv/bin/activate
```

To run the type checker (if you use VSCode you can install [MyPy extension](https://marketplace.visualstudio.com/items/?itemName=matangover.mypy), this will be very usefull):

```bash
mypy server
```

To run the linter and code formatter:

```bash
ruff check server
ruff format server
```

To run the server in develop mode:
```bash
python wsgi.py
```

## Test

The sample app also comes with a test suite to get you started, we use [Pytest](https://docs.pytest.org/en/stable/) for testing.

Make sure to install test dependencies before trying to run the tests:

```bash
poetry install --with test
```

The tests need access to a PostgreSQL database that **will be cleared** at the end of each test (look at .env file and set the test databse url and test database name).

Then just run the test suite.

```bash
pytest
```

> [!TIP]
> If you use VSCode install [Python Test Explorer](https://marketplace.visualstudio.com/items?itemName=LittleFoxTeam.vscode-python-test-adapter) extension, make sure that you are running only one time each test, otherwise the tests must be fail.
