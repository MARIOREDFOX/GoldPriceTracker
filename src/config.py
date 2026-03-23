# src/config.py — App-wide constants

# ── Target URL ─────────────────────────────────────────────────────────────────
URL = "https://timesofindia.indiatimes.com/business/gold-rates-today/gold-price-in-chennai"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-IN,en;q=0.9",
}

REQUEST_TIMEOUT = 15  # seconds

# ── Window ────────────────────────────────────────────────────────────────────
APP_TITLE  = "🪙 Gold Price Tracker — Chennai"
WIN_SIZE   = "1100x800"
WIN_MIN    = (920, 700)

# ── Colours ───────────────────────────────────────────────────────────────────
BG_DARK     = "#0D0D0D"
BG_PANEL    = "#161616"
BG_CARD     = "#1E1E1E"
GOLD_BRIGHT = "#FFD700"
GOLD_DIM    = "#B8860B"
GOLD_LIGHT  = "#FFF0A0"
TEXT_WHITE  = "#F5F5F5"
TEXT_GRAY   = "#888888"
RED_DOWN    = "#FF4C4C"
GREEN_UP    = "#4CFF91"
ACCENT      = "#C9A84C"
BORDER      = "#2E2E2E"

# ── Fonts ─────────────────────────────────────────────────────────────────────
FONT_TITLE  = ("Georgia",      22, "bold")
FONT_HEAD   = ("Georgia",      13, "bold")
FONT_PRICE  = ("Courier New",  28, "bold")
FONT_LABEL  = ("Helvetica",    10)
FONT_SMALL  = ("Helvetica",     9)
FONT_MONO   = ("Courier New",  11)
