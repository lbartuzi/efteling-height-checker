# 🏰 Efteling Height Requirements Checker

A beautiful, self-updating web application that helps parents quickly determine which Efteling attractions are suitable for their children based on height and age requirements.

![Efteling](https://img.shields.io/badge/Efteling-Official%20Data-1a5f2a?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker)

## ✨ Features

### 🎢 Complete Attraction Coverage
- **34 official Efteling attractions** (exact match with Efteling.com)
- **2 shows** (Aquanura, Raveleijn) in separate section
- Direct links to official Efteling pages for each attraction

### 📊 Dynamic Data Scraping
- **Live scraping** from Efteling.com attraction pages
- Extracts height requirements, companion rules, and advisory ages
- Automatic fallback to verified baseline data if scraping fails
- **Auto-updates every 6 hours** via cron job

### 🎯 Height Categories
Filter attractions by child height:
- 95 cm, 100 cm, 110 cm, 120 cm, 130 cm, 135 cm, 140 cm

Each height shows:
- ✅ **Independent** - Can ride alone
- 👨‍👧 **With Companion** - Needs adult (16+) companion  
- ❌ **Not Available** - Too short

### 📱 User Interface
- Beautiful Efteling-themed design (green & gold)
- Fully responsive (mobile-friendly)
- Click any attraction to open official Efteling page
- Dutch attraction types shown alongside English

### 📋 Data Displayed
| Field | Description |
|-------|-------------|
| Min Height | Minimum height to ride independently |
| With Companion | Minimum height when accompanied by adult (16+) |
| Advisory Age | Recommended minimum age (e.g., 8+ for Danse Macabre) |
| Type | Attraction type in English and Dutch |
| Notes | Tips and warnings about the attraction |

---

## 🚀 Quick Start

### Using Docker Compose (Recommended)

```bash
# Clone/download the files
cd efteling-height-checker

# Build and start
docker-compose up -d

# View logs
docker-compose logs -f
```

Access at: **http://localhost:5000**

### Using Docker directly

```bash
# Build
docker build -t efteling-height-checker .

# Run
docker run -d \
  --name efteling-height-checker \
  -p 5000:5000 \
  -v efteling-data:/app/data \
  --restart unless-stopped \
  efteling-height-checker
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run initial scrape
python scraper.py

# Start web server
python app.py
```

---

## 📁 Project Structure

```
efteling-height-checker/
├── scraper.py          # Data scraper (fetches from Efteling.com)
├── app.py              # Flask web application
├── Dockerfile          # Container definition
├── docker-compose.yml  # Easy deployment config
├── entrypoint.sh       # Container startup script
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main web interface |
| `/api/data` | GET | Full JSON data (attractions, shows, categories) |
| `/api/height/<cm>` | GET | Attractions for specific height (e.g., `/api/height/120`) |
| `/api/scrape` | GET | Trigger manual data refresh |

### Example API Response

```json
{
  "total_attractions": 34,
  "total_shows": 2,
  "attractions": [
    {
      "name": "Baron 1898",
      "type": "Dive Coaster",
      "type_dutch": "Dive coaster",
      "min_height_cm": 132,
      "advisory_age": 9,
      "url": "https://www.efteling.com/en/park/attractions/baron-1898"
    }
  ],
  "shows": [
    {
      "name": "Aquanura",
      "type": "Water Show",
      "url": "https://www.efteling.com/en/park/shows/aquanura"
    }
  ]
}
```

---

## 🎢 Complete Attractions List

### Roller Coasters & Thrill Rides
| Attraction | Type (Dutch) | Min Height | With Companion | Age |
|------------|--------------|-----------|----------------|-----|
| Baron 1898 | Dive coaster | 132 cm | - | 9+ |
| Python | Stalen achtbaan | 120 cm | - | - |
| Joris en de Draak | Houten achtbaan | 120 cm | 110 cm | - |
| Vogel Rok | Overdekte achtbaan | 120 cm | - | - |
| Max & Moritz | Dubbele familie-achtbaan | 130 cm | 100 cm | - |

### Water Attractions
| Attraction | Type (Dutch) | Min Height |
|------------|--------------|-----------|
| De Vliegende Hollander | Waterachtbaan | 120 cm |
| Piraña | Wildwaterbaan | 120 cm |
| Gondoletta | Boottocht | 120 cm |

### Dark Rides & Indoor Attractions
| Attraction | Type (Dutch) | Min Height | Age |
|------------|--------------|-----------|-----|
| Danse Macabre | Spookspektakel | 120 cm | 8+ |
| Symbolica | Overdekte familie-attractie | 120 cm | - |
| Droomvlucht | Overdekte attractie | 100 cm | - |
| Fata Morgana | Overdekte attractie | 120 cm | - |
| Carnaval Festival | Overdekte attractie | 100 cm | - |
| Villa Volta | Vervloekt huis | 100 cm | - |

### Flat Rides
| Attraction | Type (Dutch) | Min Height |
|------------|--------------|-----------|
| Halve Maen | Schipschommel | 120 cm |
| Pagode | Zwevende tempel | 100 cm |
| Sirocco | Draaiende handelsschuitjes | 100 cm |

### Transport & Family Rides
| Attraction | Type (Dutch) | Min Height |
|------------|--------------|-----------|
| Stoomtrein | Rondrit door Efteling | 100 cm |
| De Monorail | Rondrit op hoogte | 120 cm |
| De Oude Tufferbaan | Oldtimerbaan | 110 cm |
| Kinderspoor | Traptreintjes | 120 cm |
| Stoomcarrousel | Draaimolen | 100 cm |
| Anton Pieckplein | Authentieke carrousels | 100 cm |

### No Height Requirement
| Attraction | Type (Dutch) |
|------------|--------------|
| Sprookjesbos | Attractie (Fairytale Forest) |
| Fabula | 4D-filmavontuur |
| Het Volk van Laaf | Bijzondere Efteling-bewoners |
| Diorama | Miniatuurwereld |
| Archipel | Avontureneiland |
| Nest! | Speelbos |
| Kindervreugd | Speeltuin |
| Kleuterhof | Speeltuin |
| Efteling Museum | Museum |
| Holle Bolle Gijs | Papierverslinder |
| Game Gallery | Speelgalerij |

### 🎭 Shows (Separate from Attractions)
| Show | Type | Notes |
|------|------|-------|
| Aquanura | Water Show | Europe's largest fountain show |
| Raveleijn | Stunt Show | Live action with horses (seasonal) |

---

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 5000 | Web server port |
| `TZ` | Europe/Amsterdam | Timezone for cron scheduling |

### Scraping Schedule

| Event | Timing |
|-------|--------|
| Container start | Immediate scrape |
| Scheduled | Every 6 hours (00:00, 06:00, 12:00, 18:00) |
| Manual | Via `/api/scrape` endpoint |

---

## 🔧 How It Works

1. **Scraper** (`scraper.py`):
   - Iterates through all 34 attraction URLs on Efteling.com
   - Parses height requirements, companion rules, advisory ages
   - Falls back to verified baseline data if page fetch fails
   - Saves JSON to `/app/data/attractions.json`

2. **Web Server** (`app.py`):
   - Flask application serving the UI
   - Reads JSON data and renders Jinja2 template
   - Categorizes attractions by height on each request

3. **Scheduling**:
   - Cron job runs scraper every 6 hours
   - Data persists in Docker volume between restarts

---

## 🐛 Troubleshooting

### No data showing?
```bash
# Check if scraper ran
docker-compose logs | grep scraper

# Manually trigger scrape
curl http://localhost:5000/api/scrape
```

### Container won't start?
```bash
# Check logs
docker-compose logs -f

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Stale data?
```bash
# Force refresh
curl http://localhost:5000/api/scrape

# Or restart container
docker-compose restart
```

---

## 📝 Data Sources

All data is scraped from official Efteling sources:

| Source | URL Pattern |
|--------|-------------|
| Attractions | `https://www.efteling.com/en/park/attractions/{slug}` |
| Shows | `https://www.efteling.com/en/park/shows/{slug}` |

Fallback baseline data is based on official Efteling requirements as of December 2025.

---

## ⚠️ Disclaimer

This is an **unofficial tool** for planning purposes only. 

- Always verify height requirements at the park
- Requirements may change without notice
- Use the official Efteling app for real-time information
- This project is not affiliated with Efteling

---

## 📄 License

MIT License - Feel free to use and modify for personal use.

---

## 🙏 Acknowledgments

- [Efteling](https://www.efteling.com) - For creating magical experiences for over 70 years
- Efteling fan communities for height requirement documentation and verification

---

<p align="center">
  <strong>Made with ❤️ for Efteling families</strong>
  <br><br>
  🎢🏰✨
</p>
