#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "-----> Installing Python dependencies"
pip install --upgrade pip
pip install -r requirements.txt

echo "-----> Setting up environment"
export PYTHONUNBUFFERED=1
export PYTHONHASHSEED=random

# Create necessary directories
echo "-----> Creating required directories"
mkdir -p logs

# Run database migrations if needed
echo "-----> Running database migrations"
if [ -f "alembic.ini" ]; then
    python -m alembic upgrade head
else
    echo "No alembic.ini found, skipping migrations"
fi

echo "-----> Setup completed successfully"
