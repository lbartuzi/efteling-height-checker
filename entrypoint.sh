#!/bin/bash

echo "Starting Efteling Height Requirements Service..."

# Create log files
touch /var/log/scraper.log
touch /var/log/wait_times.log

# Run initial height requirements scrape
echo "Running initial data scrape..."
python /app/scraper.py

# Run initial wait times fetch
echo "Running initial wait times fetch..."
python /app/wait_times.py || echo "Wait times fetch failed (park may be closed)"

# Start cron daemon in background
echo "Starting cron scheduler..."
cron

# Start web server with gunicorn
echo "Starting web server on port ${PORT:-5000}..."
exec gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 2 --timeout 120 app:app
