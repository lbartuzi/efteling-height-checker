FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    cron \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY scraper.py .
COPY wait_times.py .
COPY app.py .
COPY entrypoint.sh .

# Create data directory
RUN mkdir -p /app/data

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Setup cron jobs
# Height requirements: every 6 hours
# Wait times: every 5 minutes during park hours (9:00-23:00 Amsterdam time)
RUN echo "0 */6 * * * cd /app && /usr/local/bin/python /app/scraper.py >> /var/log/scraper.log 2>&1" > /etc/cron.d/efteling-cron && \
    echo "*/5 9-23 * * * cd /app && /usr/local/bin/python /app/wait_times.py >> /var/log/wait_times.log 2>&1" >> /etc/cron.d/efteling-cron && \
    chmod 0644 /etc/cron.d/efteling-cron && \
    crontab /etc/cron.d/efteling-cron

# Expose port
EXPOSE 5000

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=5000
ENV TZ=Europe/Amsterdam

# Run entrypoint
CMD ["/app/entrypoint.sh"]
