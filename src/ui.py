# src/ui.py — Tkinter UI: widgets, layout, update methods

import tkinter as tk
from tkinter import messagebox
from datetime import datetime

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

from src import config as C


# ── Helper: labelled separator ────────────────────────────────────────────────
def _hsep(parent, color=C.BORDER):
    tk.Frame(parent, bg=color, height=1).pack(fill="x", padx=0, pady=2)


# ── Top bar ───────────────────────────────────────────────────────────────────
class TopBar(tk.Frame):
    def __init__(self, master, on_refresh):
        super().__init__(master, bg=C.BG_DARK, pady=12)
        self.pack(fill="x", padx=20)

        tk.Label(self, text="🪙", font=("Helvetica", 28),
                 bg=C.BG_DARK, fg=C.GOLD_BRIGHT).pack(side="left")

        info = tk.Frame(self, bg=C.BG_DARK)
        info.pack(side="left", padx=10)
        tk.Label(info, text="GOLD PRICE TRACKER", font=C.FONT_TITLE,
                 bg=C.BG_DARK, fg=C.GOLD_BRIGHT).pack(anchor="w")
        self.lbl_date = tk.Label(info, text="Initialising…",
                                 font=C.FONT_SMALL, bg=C.BG_DARK, fg=C.TEXT_GRAY)
        self.lbl_date.pack(anchor="w")

        self.btn_refresh = tk.Button(
            self, text="⟳  Refresh", font=C.FONT_LABEL,
            bg=C.ACCENT, fg=C.BG_DARK, relief="flat",
            padx=14, pady=6, cursor="hand2", command=on_refresh,
        )
        self.btn_refresh.pack(side="right")

    def set_date(self, text):
        self.lbl_date.config(text=text)

    def set_busy(self, busy: bool):
        self.btn_refresh.config(state="disabled" if busy else "normal")


# ── Status bar ────────────────────────────────────────────────────────────────
class StatusBar(tk.Label):
    def __init__(self, master):
        super().__init__(master, text="⏳ Loading…",
                         font=C.FONT_LABEL, bg=C.BG_DARK, fg=C.GOLD_DIM,
                         anchor="w", padx=20)
        self.pack(fill="x", pady=3)

    def info(self, msg):   self.config(text=msg, fg=C.GOLD_DIM)
    def ok(self, msg):     self.config(text=msg, fg=C.GREEN_UP)
    def error(self, msg):  self.config(text=msg, fg=C.RED_DOWN)


# ── Price Cards ───────────────────────────────────────────────────────────────
class PriceCards(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=C.BG_DARK)
        self.pack(fill="x", padx=20, pady=(4, 0))
        self._vars = {}
        for k in ("18K", "22K", "24K"):
            card = tk.Frame(self, bg=C.BG_CARD, padx=18, pady=14,
                            highlightbackground=C.GOLD_DIM, highlightthickness=1)
            card.pack(side="left", expand=True, fill="both", padx=6)
            tk.Label(card, text=f"{k}  Gold / gram", font=C.FONT_LABEL,
                     bg=C.BG_CARD, fg=C.TEXT_GRAY).pack(anchor="w")
            pv = tk.StringVar(value="—")
            cv = tk.StringVar(value="")
            tk.Label(card, textvariable=pv, font=C.FONT_PRICE,
                     bg=C.BG_CARD, fg=C.GOLD_BRIGHT).pack(anchor="w")
            chg = tk.Label(card, textvariable=cv, font=C.FONT_LABEL,
                           bg=C.BG_CARD, fg=C.TEXT_GRAY)
            chg.pack(anchor="w")
            self._vars[k] = (pv, cv, chg)

    def update(self, prices: dict, changes: dict):
        for k, (pv, cv, chg_lbl) in self._vars.items():
            if k in prices:
                pv.set(f"₹{prices[k]:,}")
                ch = changes.get(k, 0)
                if ch < 0:
                    cv.set(f"▼  ₹{abs(ch):,}  today")
                    chg_lbl.config(fg=C.RED_DOWN)
                elif ch > 0:
                    cv.set(f"▲  ₹{ch:,}  today")
                    chg_lbl.config(fg=C.GREEN_UP)
                else:
                    cv.set("No change today")
                    chg_lbl.config(fg=C.TEXT_GRAY)
            else:
                pv.set("N/A")
                cv.set("")


# ── Trend Graph ───────────────────────────────────────────────────────────────
class TrendGraph(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=C.BG_PANEL, padx=12, pady=10,
                         highlightbackground=C.BORDER, highlightthickness=1)
        tk.Label(self, text="📈  30-Day Price Trend", font=C.FONT_HEAD,
                 bg=C.BG_PANEL, fg=C.GOLD_BRIGHT).pack(anchor="w", pady=(0, 4))
        self._canvas_frame = tk.Frame(self, bg=C.BG_PANEL)
        self._canvas_frame.pack(fill="both", expand=True)
        tk.Label(self._canvas_frame, text="Graph will appear after data loads…",
                 font=C.FONT_SMALL, bg=C.BG_PANEL, fg=C.TEXT_GRAY).pack(expand=True)

    def update(self, trend: list):
        for w in self._canvas_frame.winfo_children():
            w.destroy()

        if not trend:
            tk.Label(self._canvas_frame, text="No trend data available.",
                     font=C.FONT_SMALL, bg=C.BG_PANEL, fg=C.TEXT_GRAY).pack(expand=True)
            return

        dates = [r["date"] for r in trend]
        p22   = [r["22K"]  for r in trend]
        p24   = [r["24K"]  for r in trend]

        fig = Figure(figsize=(6, 3.4), dpi=90, facecolor=C.BG_PANEL)
        ax  = fig.add_subplot(111)
        ax.set_facecolor(C.BG_CARD)

        ax.fill_between(dates, p22, alpha=0.15, color=C.GOLD_DIM)
        ax.fill_between(dates, p24, alpha=0.10, color=C.GOLD_BRIGHT)
        ax.plot(dates, p22, color=C.GOLD_DIM,    lw=2, marker="o", ms=3.5, label="22K")
        ax.plot(dates, p24, color=C.GOLD_BRIGHT, lw=2, marker="o", ms=3.5, label="24K")

        if dates:
            ax.annotate(f"₹{p22[-1]:,}", xy=(dates[-1], p22[-1]),
                        xytext=(5, 4), textcoords="offset points",
                        fontsize=7, color=C.GOLD_DIM)
            ax.annotate(f"₹{p24[-1]:,}", xy=(dates[-1], p24[-1]),
                        xytext=(5, -12), textcoords="offset points",
                        fontsize=7, color=C.GOLD_BRIGHT)

        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        fig.autofmt_xdate(rotation=35, ha="right")
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"₹{int(x):,}"))
        ax.tick_params(colors=C.TEXT_GRAY, labelsize=7)
        for spine in ax.spines.values():
            spine.set_edgecolor(C.BORDER)
        ax.grid(color=C.BORDER, linestyle="--", lw=0.5, alpha=0.7)
        ax.legend(facecolor=C.BG_CARD, edgecolor=C.BORDER,
                  labelcolor=C.TEXT_WHITE, fontsize=8)
        fig.tight_layout(pad=1.2)

        canvas = FigureCanvasTkAgg(fig, master=self._canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


# ── News Panel ────────────────────────────────────────────────────────────────
class NewsPanel(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=C.BG_PANEL, padx=10, pady=10,
                         highlightbackground=C.BORDER, highlightthickness=1)
        tk.Label(self, text="📰  Market Summary", font=C.FONT_HEAD,
                 bg=C.BG_PANEL, fg=C.GOLD_BRIGHT).pack(anchor="w", pady=(0, 4))
        self._txt = tk.Text(self, height=8, wrap="word",
                            bg=C.BG_CARD, fg=C.TEXT_WHITE, font=C.FONT_SMALL,
                            relief="flat", bd=4, state="disabled",
                            selectbackground=C.ACCENT)
        self._txt.pack(fill="x")

    def update(self, text: str):
        self._txt.config(state="normal")
        self._txt.delete("1.0", "end")
        self._txt.insert("end", text or "No summary available.")
        self._txt.config(state="disabled")


# ── March Stats Panel ─────────────────────────────────────────────────────────
class StatsPanel(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=C.BG_PANEL, padx=10, pady=10,
                         highlightbackground=C.BORDER, highlightthickness=1)
        tk.Label(self, text="📊  March 2026 Stats", font=C.FONT_HEAD,
                 bg=C.BG_PANEL, fg=C.GOLD_BRIGHT).pack(anchor="w", pady=(0, 4))
        self._body = tk.Frame(self, bg=C.BG_PANEL)
        self._body.pack(fill="x")

    def update(self, stats: dict):
        for w in self._body.winfo_children():
            w.destroy()
        if not stats:
            tk.Label(self._body, text="No stats available.",
                     font=C.FONT_SMALL, bg=C.BG_PANEL, fg=C.TEXT_GRAY).pack()
            return
        for ci, txt in enumerate(("Metric", "22K", "24K")):
            tk.Label(self._body, text=txt,
                     font=(C.FONT_SMALL[0], C.FONT_SMALL[1], "bold"),
                     bg=C.BG_PANEL, fg=C.ACCENT, width=15, anchor="w"
                     ).grid(row=0, column=ci, padx=2)
        for i, (lbl, vals) in enumerate(stats.items()):
            rbg = C.BG_CARD if i % 2 == 0 else C.BG_PANEL
            tk.Label(self._body, text=lbl, font=C.FONT_SMALL,
                     bg=rbg, fg=C.TEXT_GRAY, width=15, anchor="w"
                     ).grid(row=i+1, column=0, padx=2)
            for j, k in enumerate(("22K", "24K")):
                v = vals.get(k, "-")
                fg = C.RED_DOWN if "Falling" in v else (
                     C.GREEN_UP if "Rising" in v else C.GOLD_LIGHT)
                tk.Label(self._body, text=v, font=C.FONT_MONO,
                         bg=rbg, fg=fg, width=15, anchor="w"
                         ).grid(row=i+1, column=j+1, padx=2)


# ── Daily Table ───────────────────────────────────────────────────────────────
class DailyTable(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=C.BG_PANEL, padx=12, pady=8,
                         highlightbackground=C.BORDER, highlightthickness=1)
        tk.Label(self, text="🗓  Recent Daily Prices", font=C.FONT_HEAD,
                 bg=C.BG_PANEL, fg=C.GOLD_BRIGHT).pack(anchor="w", pady=(0, 4))
        self._body = tk.Frame(self, bg=C.BG_PANEL)
        self._body.pack(fill="x")

    def update(self, trend: list):
        for w in self._body.winfo_children():
            w.destroy()
        recent = trend[-10:] if len(trend) >= 10 else trend
        if not recent:
            tk.Label(self._body, text="No data available.",
                     font=C.FONT_SMALL, bg=C.BG_PANEL, fg=C.TEXT_GRAY).pack()
            return
        for ci, (hdr, w) in enumerate([("Date", 18), ("22K / gm (₹)", 16), ("24K / gm (₹)", 16)]):
            tk.Label(self._body, text=hdr,
                     font=(C.FONT_SMALL[0], C.FONT_SMALL[1], "bold"),
                     bg=C.BG_PANEL, fg=C.ACCENT, width=w, anchor="w"
                     ).grid(row=0, column=ci, padx=4, pady=2)
        for ri, row in enumerate(reversed(recent)):
            rbg = C.BG_CARD if ri % 2 == 0 else C.BG_PANEL
            tk.Label(self._body, text=row["date"].strftime("%d %b %Y"),
                     font=C.FONT_SMALL, bg=rbg, fg=C.TEXT_WHITE,
                     width=18, anchor="w").grid(row=ri+1, column=0, padx=4)
            tk.Label(self._body, text=f"{row['22K']:,}",
                     font=C.FONT_MONO, bg=rbg, fg=C.GOLD_DIM,
                     width=16, anchor="w").grid(row=ri+1, column=1, padx=4)
            tk.Label(self._body, text=f"{row['24K']:,}",
                     font=C.FONT_MONO, bg=rbg, fg=C.GOLD_BRIGHT,
                     width=16, anchor="w").grid(row=ri+1, column=2, padx=4)
