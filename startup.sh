#!/bin/bash

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install requirements
pip install --upgrade pip
pip install -r requirements-pa.txt

# Set environment variables
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Create necessary directories
mkdir -p logs

# Make the script executable
chmod +x startup.sh
