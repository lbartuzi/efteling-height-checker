#!/bin/bash

echo "Starting Efteling Height Requirements Service..."

# Create log file
touch /var/log/scraper.log

# Run initial scrape
echo "Running initial data scrape..."
python /app/scraper.py

# Start cron daemon in background
echo "Starting cron scheduler..."
cron

# Start web server with gunicorn
echo "Starting web server on port ${PORT:-5000}..."
exec gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 2 --timeout 120 app:app
