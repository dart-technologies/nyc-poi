#!/bin/bash
# MongoDB POI Import Helper
# Loads environment variables and runs import

echo "Loading environment variables from .env..."

# Load .env file
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Environment variables loaded"
else
    echo "❌ .env file not found!"
    echo "Please create .env file with your MongoDB URI"
    exit 1
fi

# Run import script
echo ""
python3 import_pois.py
