#!/usr/bin/env python3
"""
main.py — Entry point for Gold Price Tracker
---------------------------------------------
Run:
    python3 main.py

First time? Run the installer first:
    python3 install.py
"""

import sys
import os

# Make sure src/ is importable when running from the project root
sys.path.insert(0, os.path.dirname(__file__))

# ── Dependency gate ───────────────────────────────────────────────────────────
MISSING = []
for pkg, mod in [("requests", "requests"), ("beautifulsoup4", "bs4"),
                 ("matplotlib", "matplotlib")]:
    try:
        __import__(mod)
    except ImportError:
        MISSING.append(pkg)

if MISSING:
    print("=" * 54)
    print("  Missing dependencies detected!")
    print("  Please run the installer first:")
    print()
    print("      python3 install.py")
    print()
    print("  Or install manually:")
    print(f"      pip install {' '.join(MISSING)}")
    print("=" * 54)
    sys.exit(1)

# ── Launch ────────────────────────────────────────────────────────────────────
from src.app import GoldApp

if __name__ == "__main__":
    app = GoldApp()
    app.mainloop()
