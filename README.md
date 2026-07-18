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
7. [Permissions](#permissions)

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

The tests need access to a PostgreSQL database (look at .env file and set the test databse url and test database name). Each test runs inside its own database transaction (with a SAVEPOINT, so a test's own `commit()` calls don't escape it) that is **rolled back** right after the test finishes, instead of truncating the whole database — this keeps every test isolated while staying fast regardless of how many tables the schema has.

Then just run the test suite.

```bash
pytest
```

> [!TIP]
> If you use VSCode install [Python Test Explorer](https://marketplace.visualstudio.com/items?itemName=LittleFoxTeam.vscode-python-test-adapter) extension, make sure that you are running only one time each test, otherwise the tests must be fail.

## Permissions

USPolis uses a role-based permission system: a `Role` groups a set of `Permission`s (`BuildingPermission`, `ClassroomPermission`, `CoursePermission`) and is assigned to `User`s via `/admin/roles`. A permission is always granted to a role — there is no way to grant a permission directly to a single user ("point permissions") anymore, every `Permission` row requires a `role_id`.

- Each permission scopes a set of `action`s (`CREATE`, `READ`, `UPDATE`, `DELETE`, and for `BUILDING`/`CLASSROOM` also `ALLOCATE`/`RESERVE`) to a resource (`BUILDING`, `CLASSROOM`, `COURSE`), either a specific instance (`resource_id`) or a wildcard (`resource_id = -1` in requests, stored as `NULL`) meaning "every instance of that resource".
- A `BuildingPermission` cascades down to every `Classroom` inside that building for the same action, so granting e.g. `ALLOCATE` on a building lets a role allocate any room in it without needing one `ClassroomPermission` per room.
- A wildcard grant (no specific building/classroom/course) is only honored for `UPDATE`, `DELETE`, `ALLOCATE`, and `RESERVE` when the requesting user is an admin — a non-admin role can never be granted "update/delete/allocate/reserve everything in the system at once" through a wildcard permission, only through a building- or resource-scoped one. `CREATE`/`READ` wildcards are honored for any role.
- Manage roles and permissions via the `/admin/roles` and `/admin/permissions` endpoints (see `server/routes/admin/roles_admin_routes.py` and `server/routes/admin/permissions_admin_routes.py`).

> [!NOTE]
> Wiring these permissions into per-request enforcement on every resource endpoint (and retiring the older `Group`-based access model it's replacing) is in progress on the `feature/role-based-permissions` branch — today the `Role`/`Permission` data model and its admin CRUD endpoints exist, but request-time authorization still runs on `Group` membership.
