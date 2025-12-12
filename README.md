# Efteling Height Requirements Checker 🏰🎢

A web application that scrapes and displays Efteling theme park attraction height requirements, helping parents quickly determine which rides are suitable for their children.

## Features

- 🔄 **Automatic scraping** every 6 hours from multiple sources
- 🎨 **Beautiful responsive UI** with Efteling-inspired design
- 👶🧒👦 **Quick height filters** for 95cm, 120cm, and 135cm
- 📊 **Complete attraction table** with all requirements
- 📚 **Source tracking** with status indicators
- 🔌 **JSON API** for programmatic access

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Clone or copy files to your server
cd efteling-height-checker

# Build and run
docker-compose up -d

# View logs
docker-compose logs -f
```

The application will be available at `http://localhost:5000`

### Using Docker directly

```bash
# Build the image
docker build -t efteling-height-checker .

# Run the container
docker run -d \
  --name efteling-height-checker \
  -p 5000:5000 \
  -v efteling-data:/app/data \
  efteling-height-checker
```

### Running locally (development)

```bash
# Install dependencies
pip install -r requirements.txt

# Run initial scrape
python scraper.py

# Start the web server
python app.py
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Main web interface |
| `GET /api/data` | Full JSON data |
| `GET /api/height/<cm>` | Attractions for specific height (95, 120, 135) |
| `GET /api/scrape` | Trigger manual scrape |

## Data Sources

The scraper collects data from:

1. **Efteling Official** - https://www.efteling.com/en/park/attractions
2. **Our Departure Board** - Comprehensive height requirement list
3. **Vacatis** - Ride information and restrictions
4. **Theme Park Insider** - Park reviews and attraction details

## Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 5000 | Web server port |
| `TZ` | Europe/Amsterdam | Timezone for cron |

## File Structure

```
efteling-height-checker/
├── app.py              # Flask web application
├── scraper.py          # Data scraper
├── Dockerfile          # Container definition
├── docker-compose.yml  # Docker Compose config
├── requirements.txt    # Python dependencies
├── entrypoint.sh       # Container startup script
└── README.md           # This file
```

## Scraping Schedule

The scraper runs:
- **On container start** - Initial data collection
- **Every 6 hours** - Scheduled via cron (00:00, 06:00, 12:00, 18:00)

Manual scraping can be triggered via `/api/scrape`

## Height Categories

### 95 cm (Toddlers)
- Limited to non-height restricted attractions
- Can access many attractions with adult companion (16+)

### 120 cm (Children)
- Access to almost all attractions
- Only Baron 1898 (132cm) unavailable

### 135 cm (Older Children)
- Full access to all attractions
- No restrictions

## Disclaimer

This is an unofficial tool. Always verify height requirements at the park entrance or on the official Efteling website/app before planning your visit.

## License

MIT License - Feel free to use and modify for personal use.

---

Made with ❤️ for Efteling families
