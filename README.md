# 🏰 Efteling Height Requirements & Wait Times

A beautiful, self-updating web application that helps parents plan their Efteling visit with:
- **Height requirements** for all 34 attractions
- **Live wait times** (updated every 5 minutes)
- **Access conditions** (wheelchair, pregnancy, etc.)

![Efteling](https://img.shields.io/badge/Efteling-Official%20Data-1a5f2a?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker)

## ✨ Features

### 🎢 Height Requirements
- Accurate interpretation of Efteling's access rules
- Correctly handles "supervision required" vs "minimum height"
- Categories: Independent, With Companion, Not Available

### ⏱️ Live Wait Times
- Real-time data from Queue-Times.com API
- Updates every 5 minutes during park hours (9:00-23:00)
- Shows: Open/Closed status, wait time in minutes
- Color-coded: 🟢 Normal, 🟡 Busy (20+ min), 🔴 Very Busy (45+ min)

### ♿ Access Conditions
| Icon | Meaning |
|------|---------|
| ♿ | Wheelchair accessible |
| 🔄 | Wheelchair with transfer |
| 🚫 | Not wheelchair accessible |
| 🤰 | Not for pregnant women |
| 🩹 | Not suitable with injuries |
| 📵 | Cameras not allowed |
| 🦮 | Guide dogs allowed |
| 👤 | Single rider available |
| 🌙 | Partly in the dark |
| 💦 | You may get wet |

### 🔒 Security
All 6 critical security headers included (CSP, X-Frame-Options, etc.)

---

## 🚀 Quick Start

```bash
cd efteling-height-checker
docker-compose up -d
```

Access at: **http://localhost:5000**

---

## 📁 Project Files

```
├── scraper.py          # Height requirements from Efteling.com
├── wait_times.py       # Live wait times from Queue-Times.com
├── app.py              # Flask web application
├── Dockerfile          # Container with dual cron jobs
├── docker-compose.yml  # Easy deployment
├── entrypoint.sh       # Startup script
└── requirements.txt    # Python dependencies
```

---

## 🔄 Data Update Schedule

| Data Type | Frequency | Source |
|-----------|-----------|--------|
| Height Requirements | Every 6 hours | Efteling.com |
| Wait Times | Every 5 minutes* | Queue-Times.com |

*Only during park hours (9:00-23:00 Amsterdam time)

---

## 🔌 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/` | Web interface |
| `/api/data` | Full JSON data |
| `/api/height/<cm>` | Categories for height |
| `/api/scrape` | Refresh height data |
| `/api/wait_times` | Refresh wait times |

### Example Response

```json
{
  "name": "Baron 1898",
  "min_height_cm": 132,
  "is_open": true,
  "wait_time": 35,
  "access": {
    "wheelchair": "transfer",
    "pregnant": true
  }
}
```

---

## 📊 Wait Time Display

Each attraction card shows:

| Display | Meaning |
|---------|---------|
| 🔴 Closed | Attraction is not operating |
| 🟢 Open | Operating, no wait time data |
| ⏱️ 15 min | Current wait time |
| (Yellow bg) | Wait time 20-44 minutes |
| (Red bg) | Wait time 45+ minutes |

---

## 🎢 Height Requirements Summary

### Strict Minimum (cannot ride below)
| Attraction | Min Height | Access |
|------------|-----------|--------|
| Baron 1898 | 132cm | 🔄🤰🩹📵 |
| Max & Moritz | 130cm (100cm with companion) | 🔄🤰🩹 |
| Python | 120cm | 🔄🤰🩹 |
| Joris en de Draak | 120cm (110cm with companion) | 🔄🤰🩹👤 |
| Danse Macabre | 120cm | 🔄🤰🩹🌙 |

### Supervision Below Height (no minimum)
| Attraction | Need Companion Below |
|------------|---------------------|
| Gondoletta, Stoomtrein | 120cm |
| De Oude Tufferbaan | 110cm |
| Symbolica, Droomvlucht, Fata Morgana | 100cm |
| Stoomcarrousel | 100cm (supervision only) |

---

## 📜 Attribution

Wait times data provided by:

> **[Powered by Queue-Times.com](https://queue-times.com/parks/160)**

As required by their free API terms.

---

## ⚙️ Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 5000 | Web server port |
| `TZ` | Europe/Amsterdam | Timezone for cron |

---

## 🐛 Troubleshooting

```bash
# View logs
docker-compose logs -f

# Refresh height data
curl http://localhost:5000/api/scrape

# Refresh wait times
curl http://localhost:5000/api/wait_times

# Rebuild
docker-compose down && docker-compose build --no-cache && docker-compose up -d
```

---

## ⚠️ Disclaimer

Unofficial tool for planning. Always verify at the park.

---

<p align="center">
  <strong>Made with ❤️ for Efteling families</strong><br>
  🎢🏰⏱️
</p>
