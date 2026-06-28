#!/bin/bash
echo "Building Room Dekho for Vercel..."

# Install dependencies
python3 -m pip install -r requirements.txt

# Collect static files
python3 manage.py collectstatic --noinput

echo "Build complete!"
