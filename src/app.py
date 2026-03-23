# src/app.py — GoldApp: main Tk window, wires ui + scraper together

import tkinter as tk
from tkinter import messagebox
import threading
from datetime import datetime

from src import config as C
from src.scraper import scrape_gold_data
from src.ui import (
    TopBar, StatusBar, PriceCards,
    TrendGraph, NewsPanel, StatsPanel, DailyTable,
)


class GoldApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(C.APP_TITLE)
        self.geometry(C.WIN_SIZE)
        self.minsize(*C.WIN_MIN)
        self.configure(bg=C.BG_DARK)
        self._build_ui()
        # Kick off first fetch after window is ready
        self.after(200, self._start_fetch)

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Top bar with title + refresh button
        self._topbar   = TopBar(self, on_refresh=self._start_fetch)

        # Thin gold separator
        tk.Frame(self, bg=C.GOLD_DIM, height=1).pack(fill="x", padx=20)

        # Status text
        self._statusbar = StatusBar(self)

        # Price cards (18K / 22K / 24K)
        self._cards = PriceCards(self)

        # Main body: graph (left) + sidebar (right)
        body = tk.Frame(self, bg=C.BG_DARK)
        body.pack(fill="both", expand=True, padx=20, pady=8)

        self._graph = TrendGraph(body)
        self._graph.pack(side="left", fill="both", expand=True)

        sidebar = tk.Frame(body, bg=C.BG_DARK, width=310)
        sidebar.pack(side="right", fill="y", padx=(10, 0))
        sidebar.pack_propagate(False)

        self._news  = NewsPanel(sidebar)
        self._news.pack(fill="x")

        self._stats = StatsPanel(sidebar)
        self._stats.pack(fill="x", pady=(10, 0))

        # Bottom daily table
        self._table = DailyTable(self)
        self._table.pack(fill="x", padx=20, pady=(0, 12))

    # ── Data Fetch ────────────────────────────────────────────────────────────
    def _start_fetch(self):
        self._statusbar.info("⏳  Fetching live gold prices…")
        self._topbar.set_busy(True)
        threading.Thread(target=self._fetch_worker, daemon=True).start()

    def _fetch_worker(self):
        try:
            data = scrape_gold_data()
            self.after(0, lambda: self._on_data(data))
        except Exception as exc:
            self.after(0, lambda: self._on_error(str(exc)))

    # ── Callbacks ─────────────────────────────────────────────────────────────
    def _on_data(self, data: dict):
        now = datetime.now().strftime("%H:%M:%S")
        self._topbar.set_date(f"Last updated: {data['date']}  —  {now}")
        self._topbar.set_busy(False)
        self._statusbar.ok("✅  Data loaded successfully")

        self._cards.update(data["prices"], data["changes"])
        self._news.update(data["news_text"])
        self._stats.update(data["march_stats"])
        self._table.update(data["monthly_trend"])
        self._graph.update(data["monthly_trend"])

    def _on_error(self, msg: str):
        self._statusbar.error(f"❌  {msg}")
        self._topbar.set_busy(False)
        messagebox.showerror("Fetch Error", f"Could not load data:\n\n{msg}")
