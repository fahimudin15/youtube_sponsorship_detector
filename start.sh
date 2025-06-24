#!/bin/bash
set -e

# Run database migrations if needed
if [ -f "alembic.ini" ]; then
    echo "-----> Running database migrations"
    python -m alembic upgrade head
fi

# Start the application
echo "-----> Starting application"
exec gunicorn src.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:${PORT:-8000} \
    --timeout 120 \
    --keep-alive 5 \
    --access-logfile - \
    --error-logfile -
