#!/bin/bash

# Exit immediately if any command fails
set -e

echo "🔹 Removing old virtual environment..."
rm -rf venv

echo "🔹 Creating new virtual environment..."
python3 -m venv venv

echo "🔹 Activating virtual environment..."
source venv/bin/activate

echo "🔹 Upgrading pip..."
pip install --upgrade pip

echo "🔹 Installing dependencies..."
# Adjust the requirements file if needed
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
fi

echo "🔹 Installing dev dependencies..."
pip install pytest pytest-django factory_boy python-dotenv

echo "🔹 All set! Run tests with:"
echo "source venv/bin/activate && pytest backend/"
