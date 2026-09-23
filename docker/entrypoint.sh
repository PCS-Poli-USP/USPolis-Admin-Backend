#!/usr/bin/env bash
set -euo pipefail
cd /app/backend

# server/config.py (python-decouple) does an unconditional open() on whichever
# of .env / .env.dev / .env.prod / .env.stage ENVIRONMENT selects — it raises
# FileNotFoundError if that file doesn't literally exist, even though real
# values below are supplied via container env vars (decouple checks
# os.environ before falling back to the file). These are all gitignored, so a
# fresh build context never has them — touch empty placeholders so the import
# doesn't crash; content is irrelevant.
for f in .env .env.dev .env.prod .env.stage; do
  [ -f "$f" ] || touch "$f"
done

environment_lower="$(printf '%s' "${ENVIRONMENT:-development}" | tr '[:upper:]' '[:lower:]')"

# wsgi.py (used for dev/staging) unconditionally loads certs/{key,cert}.pem
# and runs with reload=True. Generate a self-signed pair on first run if
# they're missing, using the same command already documented for local dev.
if [[ "$environment_lower" == "development" || "$environment_lower" == "staging" ]]; then
  if [[ ! -f certs/cert.pem || ! -f certs/key.pem ]]; then
    mkdir -p certs
    openssl req -x509 -newkey rsa:4096 -keyout certs/key.pem -out certs/cert.pem \
      -days 365 -nodes -subj "/CN=localhost"
  fi
fi

# Wait for Postgres to accept connections (tenacity retry inside the script,
# up to 5 minutes), then a create_all() fallback for anything Alembic hasn't
# covered yet.
python -m server.scripts.pre_start

# The only schema-creation path actually used in practice.
python -m alembic upgrade head

# Idempotent — only creates the user if FIRST_SUPERUSER_EMAIL doesn't already
# exist. Off by default so it never runs unintentionally in prod.
if [[ "${SEED_INITIAL_DATA:-false}" == "true" ]]; then
  python -m server.scripts.initial_data
fi

case "${1:-dev}" in
  dev)
    exec python wsgi.py
    ;;
  prod)
    exec gunicorn asgi:app \
      --forwarded-allow-ips="${GUNICORN_FORWARDED_ALLOW_IPS:-*}" \
      --workers "${GUNICORN_WORKERS:-4}" \
      --worker-class uvicorn.workers.UvicornWorker \
      --bind "0.0.0.0:${PORT:-5000}" \
      --timeout 120
    ;;
  *)
    exec "$@"
    ;;
esac
