# 🪙 Gold Price Tracker — Chennai

A Python desktop app that scrapes live gold prices from Times of India
and displays them in a clean dark-themed window with a 30-day trend graph.

---

## 📁 Project Structure

```
gold_tracker/
├── main.py              ← Entry point (run this)
├── install.py           ← One-time setup script
├── requirements.txt     ← Python dependencies
├── README.md
└── src/
    ├── __init__.py
    ├── config.py        ← All constants (colours, fonts, URL)
    ├── scraper.py       ← Web scraping logic (requests + BeautifulSoup)
    ├── ui.py            ← All Tkinter widget classes
    └── app.py           ← Main application window (wires everything)
```

---

## 🚀 Quick Start

### Step 1 — Install (once)
```bash
python3 install.py
```

This will:
- Check Python 3.8+
- Install all dependencies from `requirements.txt`
- Create a desktop launcher (`~/Desktop/gold_tracker.desktop`)

### Step 2 — Run
```bash
python3 main.py
```

Or double-click `gold_tracker.desktop` on your Linux desktop.

---

## 📦 Dependencies

| Package        | Version  | Purpose                     |
|----------------|----------|-----------------------------|
| requests       | 2.31.0   | HTTP fetching                |
| beautifulsoup4 | 4.12.3   | HTML parsing                 |
| matplotlib     | 3.8.4    | 30-day trend graph           |
| tkinter        | built-in | GUI window                   |

---

## ✨ Features

- **Live prices** — 18K, 22K, 24K gold per gram in ₹
- **Daily change** — colour-coded ▼ red / ▲ green vs yesterday
- **30-day graph** — area + line chart for 22K and 24K
- **Market summary** — scraped news text from TOI
- **March 2026 stats** — highest, lowest, % change
- **Recent daily table** — last 10 days of prices
- **Refresh button** — re-scrape on demand

---

## 🐧 Making It Double-Clickable

After running `install.py`, a `.desktop` file is created automatically.
If you need to create it manually:

```ini
[Desktop Entry]
Type=Application
Name=Gold Price Tracker
Exec=python3 /full/path/to/gold_tracker/main.py
Icon=utilities-finance
Terminal=false
```

Save as `~/Desktop/gold_tracker.desktop`, then:
```bash
chmod +x ~/Desktop/gold_tracker.desktop
```
