#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Change directory to the directory of the script.
cd "$(dirname "$0")"

# Set the PYTHONPATH environment variable to include the src directory.
export PYTHONPATH="$PWD/src:$PYTHONPATH"
echo "PYTHONPATH set to: $PYTHONPATH"

# Create a virtual environment named 'venv'.
virtualenv venv

# Activate the virtual environment.
source venv/bin/activate

# Install the required packages from the requirements.txt file.
pip install -r ./src/requirements.txt

# Discover and run unittests in the 'tests' directory.
python -m unittest discover ./tests

# Run the Flask application
python src/api.py
