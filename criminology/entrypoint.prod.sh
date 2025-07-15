#!/usr/bin/env bash
set -e

# List of allowed one-off Django management commands
ALLOWED_COMMANDS=("generate_secret_key" "createsuperuser" "collectstatic" "setup_periodic_tasks")

if [[ $# -gt 0 ]]; then
  if [[ " ${ALLOWED_COMMANDS[@]} " =~ " $1 " ]]; then
    if [[ "$1" == "createsuperuser" || "$1" == "setup_periodic_tasks" ]]; then
      echo "Applying database migrations before running '$1'..."
      python manage.py migrate --noinput
    fi

    if [[ "$1" == "collectstatic" ]]; then
      echo "Collecting Static Files..."
      exec python manage.py collectstatic --noinput
    else
      echo "Running Django command: $@"
      exec python manage.py "$@"
    fi
  else
    echo "Command '$1' is not allowed."
    echo "Allowed commands: ${ALLOWED_COMMANDS[*]}"
    exit 1
  fi
else
  echo "Applying database migrations..."
  python manage.py migrate --noinput

  echo "Starting Gunicorn server..."
  exec gunicorn criminology.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --access-logfile - \
    --timeout 120
fi
