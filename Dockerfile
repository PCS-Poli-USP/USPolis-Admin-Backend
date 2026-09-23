# syntax=docker/dockerfile:1

# Playwright's own image ships the exact OS packages/fonts that Chromium needs
# for this Playwright version — server/services/jupiter_crawler/authenticated_crawler.py
# uses Playwright at runtime (not just in tests), so a real headless browser has
# to be available in every stage below, not just installed as a pip package.
# The `-noble` tag (Ubuntu 24.04) ships Python 3.12, matching `requires-python`
# in pyproject.toml; keep the tag version in sync with the `playwright` version
# pinned in poetry.lock.
FROM mcr.microsoft.com/playwright/python:v1.59.0-noble AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Pin to the exact Poetry version that generated poetry.lock (see its header).
RUN pip install --no-cache-dir "poetry==2.1.2"

WORKDIR /app/backend

# Copy only the dependency manifests first so this layer is cached across
# rebuilds that don't touch dependencies.
COPY pyproject.toml poetry.lock ./

FROM base AS deps-dev
RUN poetry install --with dev,test --no-root --no-cache

FROM base AS deps-prod
RUN poetry install --without dev,test --no-root --no-cache

# ---- dev: full source tree, hot-reload via wsgi.py's reload=True ----
FROM deps-dev AS dev

COPY . .
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 5000
ENTRYPOINT ["/entrypoint.sh"]
CMD ["dev"]

# ---- prod: only what the running app needs, non-root user ----
FROM deps-prod AS prod

COPY server/ server/
COPY migrations/ migrations/
COPY asgi.py wsgi.py alembic.ini ./
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh \
    && chown -R pwuser:pwuser /app/backend

# `pwuser` is pre-created by the Playwright base image specifically for
# running browsers as non-root, with correct permissions already set up on
# its baked-in Chromium install — safer than creating a fresh user, which
# would need to be individually verified to actually have access to that
# install path. The crawler already launches Chromium with `--no-sandbox`
# (server/services/jupiter_crawler/authenticated_crawler.py), so this isn't
# relying on Chromium's own OS sandbox working across the user switch.
USER pwuser

EXPOSE 5000
ENTRYPOINT ["/entrypoint.sh"]
CMD ["prod"]
