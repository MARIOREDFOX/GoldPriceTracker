# src/scraper.py — Web scraping logic for Times of India gold price page

import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from src.config import URL, HEADERS, REQUEST_TIMEOUT


# ── Helpers ───────────────────────────────────────────────────────────────────

def _parse_price(text: str) -> int:
    """Remove Indian formatting commas and currency symbols, return int."""
    clean = text.strip().replace(",", "").replace("₹", "").replace(" ", "")
    digits = re.sub(r"[^\d]", "", clean)
    return int(digits) if digits else 0


def _parse_date(text: str) -> datetime | None:
    """
    Try multiple ordinal date formats used by TOI:
    e.g. "23rd Mar 2026", "1st Mar 2026", "22nd Mar 2026"
    """
    text = text.strip()
    for fmt in ("%dth %b %Y", "%dst %b %Y", "%dnd %b %Y", "%drd %b %Y"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


# ── Main Scrape Function ──────────────────────────────────────────────────────

def scrape_gold_data() -> dict:
    """
    Fetch and parse the TOI Chennai gold price page.

    Returns a dict with keys:
        date          str        — display date from the page
        prices        dict       — {"18K": int, "22K": int, "24K": int}
        changes       dict       — {"18K": int, "22K": int, "24K": int}  (negative = down)
        news_text     str        — market summary paragraph
        monthly_trend list[dict] — [{"date": datetime, "22K": int, "24K": int}, ...]
        march_stats   dict       — {"Metric": {"22K": str, "24K": str}, ...}
        city_rates    list[dict] — [{"city": str, "22K": int, "24K": int}, ...]
    """
    resp = requests.get(URL, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    data = {
        "date":          "N/A",
        "prices":        {},
        "changes":       {},
        "news_text":     "",
        "monthly_trend": [],
        "march_stats":   {},
        "city_rates":    [],
    }

    # ── Date ──────────────────────────────────────────────────────────────────
    date_el = soup.find("span", class_="SsOuC")
    if date_el:
        data["date"] = date_el.get_text(strip=True).replace("Date:", "").strip()

    # ── Today's Prices (kp0S_ card) ───────────────────────────────────────────
    price_card = soup.find("div", class_="kp0S_")
    if price_card:
        for item in price_card.find_all("div", class_="m05_L"):
            label_el = item.find("span", class_="wG7wj")
            if not label_el:
                continue
            carat_m = re.search(r"(\d+)K", label_el.get_text())
            if not carat_m:
                continue
            k = carat_m.group(1) + "K"
            spans = item.find_all("span")
            for sp in spans:
                if sp == label_el:
                    continue
                txt = sp.get_text(strip=True)
                if any(c.isdigit() for c in txt):
                    num = _parse_price(txt)
                    if 1000 < num < 100000 and k not in data["prices"]:
                        data["prices"][k] = num
                        break


    # ── Daily Changes (NJBta spans) ───────────────────────────────────────────
    for sp in soup.find_all("span", class_="NJBta"):
        txt = sp.get_text(strip=True)
        parent = sp.find_parent("div", class_="m05_L")
        if not parent:
            continue
        label_el = parent.find("span", class_="wG7wj")
        if not label_el:
            continue
        carat_m = re.search(r"(\d+)K", label_el.get_text())
        if not carat_m:
            continue
        k = carat_m.group(1) + "K"
        val_str = re.sub(r"[^\d\-]", "", txt.replace("₹", ""))
        try:
            data["changes"][k] = int(val_str)
        except ValueError:
            pass

    # ── News Summary ──────────────────────────────────────────────────────────
    news_div = soup.find("div", class_="u363T")
    if news_div:
        data["news_text"] = news_div.get_text(separator=" ", strip=True)[:700]

    # ── Monthly Trend Table ───────────────────────────────────────────────────
    all_rows = []
    for table_div in soup.find_all("div", class_="SDUAZ"):
        for row in table_div.find_all("div", class_="Tosh0"):
            cols = row.find_all("div", class_="JX5lj")
            if len(cols) < 3:
                continue
            date_txt = cols[0].get_text(strip=True)
            p22 = str(_parse_price(cols[1].get_text(strip=True)))
            p24 = str(_parse_price(cols[2].get_text(strip=True)))
            if not (re.search(r"\d{4}", date_txt) and p22 and p24):
                continue
            dt = _parse_date(date_txt)
            if dt:
                all_rows.append({"date": dt, "22K": int(p22), "24K": int(p24)})

    # Deduplicate and sort
    seen, unique = set(), []
    for r in all_rows:
        key = r["date"].strftime("%Y-%m-%d")
        if key not in seen:
            seen.add(key)
            unique.append(r)
    data["monthly_trend"] = sorted(unique, key=lambda x: x["date"])

    # ── March Stats (accordion) ───────────────────────────────────────────────
    for acc in soup.find_all("div", class_="accordion-item"):
        title = acc.find("div", class_="accordion-title")
        if not title or "March 2026" not in title.get_text():
            continue
        for row in acc.find_all("div", class_="Tosh0"):
            cols = row.find_all("div", class_="JX5lj")
            if len(cols) >= 3:
                lbl = cols[0].get_text(strip=True)
                data["march_stats"][lbl] = {
                    "22K": cols[1].get_text(strip=True),
                    "24K": cols[2].get_text(strip=True),
                }

    # ── City Rates Table ──────────────────────────────────────────────────────
    for table_div in soup.find_all("div", class_="SDUAZ"):
        for row in table_div.find_all("div", class_="Tosh0"):
            cols = row.find_all("div", class_="JX5lj")
            if len(cols) < 3:
                continue
            city_el = cols[0].find("a")
            if not city_el:
                continue
            city = city_el.get_text(strip=True)
            p22 = str(_parse_price(cols[1].get_text(strip=True)))
            p24 = str(_parse_price(cols[2].get_text(strip=True)))
            if city and p22 and p24:
                data["city_rates"].append({
                    "city": city,
                    "22K":  int(p22),
                    "24K":  int(p24),
                })

    return data
