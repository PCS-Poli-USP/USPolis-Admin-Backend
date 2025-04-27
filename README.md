# USPolis Backend

## Table of Contents
- [Stack](#stack)
- [Setup](#setup)
- [Run](#run)
- [Develop](#develop)
- [Test](#test)

## Stack

- [FastAPI](https://fastapi.tiangolo.com/) - Python async micro framework built on [Starlette](https://www.starlette.io/) and [PyDantic](https://docs.pydantic.dev/latest/).
- [SQL Model](https://sqlmodel.tiangolo.com/) - Python library for interacting with SQL databases, powered by [PyDantic](https://docs.pydantic.dev/latest/) and [SQLAlchemy](https://sqlalchemy.org/).
- [PostgreSQL](https://www.postgresql.org/) - Open source object-relational database. 

## Setup

This codebase was written for Python 3.11 and above. Don't forget about a venv as well. The `python` commands below assume you're pointing to your desired Python3 target.

First we'll need to install our requirements.

```bash
python -m pip install -e .
```

There are other settings in `config.py` and the included `.env` file. Assuming you've changed the SALT value, everything should run as-is if there is a local [MongoDB]() instance running ([see below](#test) for a Docker solution). Any email links will be printed to the console by default.

## Run

This sample uses [uvicorn]() as our ASGI web server. This allows us to run our server code in a much more robust and configurable environment than the development server. For example, ASGI servers let you run multiple workers that recycle themselves after a set amount of time or number of requests.

```bash
uvicorn server.main:app --reload --port 8080
```

You're API should now be available at http://localhost:8080

## Develop

This codebase is uses [mypy]() for type checking and [ruff]() for everything else. Install both with the dev tag.

```bash
python -m pip install -e .[dev]
```

To run the type checker:

```bash
mypy server
```

To run the linter and code formatter:

```bash
ruff check server
ruff format server
```

## Test

The sample app also comes with a test suite to get you started.

Make sure to install the requirements found in the test folder before trying to run the tests.

```bash
python -m pip install -e .[test]
```

The tests need access to a [MongoDB]() store that is emptied at the end of each test. The easiest way to do this is to run a Mongo container in the background.

```bash
docker run -d -p 27017:27017 mongo:7
```

You can also connect to a remote server if you're running tests in a CI/CD pipeline. Just set the `TEST_MONGO_URI` in the environment. This value defaults to localhost and is only checked in the test suite. It should **never** use your `MONGO_URI`.

Then just run the test suite.

```bash
pytest
```

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
