#!/usr/bin/env python3
"""
install.py — Gold Price Tracker Setup
--------------------------------------
Run once before first use:
    python3 install.py

What it does:
  1. Checks Python version (3.8+)
  2. Detects whether pip is available
  3. If pip is missing → creates a virtualenv (.venv/) and uses that pip
  4. If pip exists     → installs directly (no venv needed)
  5. Installs all dependencies from requirements.txt
  6. Verifies all imports work
  7. Makes main.py executable
  8. Creates a .desktop launcher that always uses the right Python
"""

import sys
import os
import subprocess
import platform

# ── Terminal colours ──────────────────────────────────────────────────────────
RESET = "\033[0m"
BOLD  = "\033[1m"
GOLD  = "\033[33m"
GREEN = "\033[32m"
RED   = "\033[31m"
CYAN  = "\033[36m"
GRAY  = "\033[90m"

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
VENV_DIR    = os.path.join(PROJECT_DIR, ".venv")


# ── Print helpers ─────────────────────────────────────────────────────────────
def banner():
    print(f"""
{GOLD}{BOLD}╔══════════════════════════════════════════╗
║   🪙  Gold Price Tracker — Installer     ║
╚══════════════════════════════════════════╝{RESET}
""")

def step(msg):  print(f"{CYAN}{BOLD}▶  {msg}{RESET}")
def ok(msg):    print(f"{GREEN}   ✔  {msg}{RESET}")
def warn(msg):  print(f"{GOLD}   ⚠  {msg}{RESET}")
def info(msg):  print(f"{GRAY}   ℹ  {msg}{RESET}")

def fail(msg):
    print(f"{RED}{BOLD}   ✘  {msg}{RESET}")
    sys.exit(1)


# ── 1. Python version ─────────────────────────────────────────────────────────
def check_python():
    step("Checking Python version...")
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 8):
        fail(f"Python 3.8+ required. You have {major}.{minor}.")
    ok(f"Python {major}.{minor} detected")


# ── 2. Detect pip / decide whether to use venv ───────────────────────────────
def has_pip(python_exe):
    result = subprocess.run(
        [python_exe, "-m", "pip", "--version"],
        capture_output=True
    )
    return result.returncode == 0


def ensure_pip_available():
    """
    Returns the Python executable that has pip.
    - If the current interpreter already has pip -> return sys.executable
    - Otherwise create .venv/ and return the venv's python
    """
    step("Checking for pip...")

    if has_pip(sys.executable):
        ok("pip found — installing to system Python")
        return sys.executable

    # pip not found -> need a venv
    warn("pip not found on this system (common on Solus / Arch / NixOS).")
    info("Creating a virtual environment in .venv/ ...")

    # Make sure venv module itself is available
    try:
        import venv  # noqa: F401
    except ImportError:
        fail(
            "Python 'venv' module is also missing.\n"
            "   On Solus run:  sudo eopkg install python3\n"
            "   Then re-run:   python3 install.py"
        )

    # Create the venv (includes its own pip via ensurepip)
    if os.path.isdir(VENV_DIR):
        info(f".venv/ already exists at {VENV_DIR} — reusing it")
    else:
        result = subprocess.run(
            [sys.executable, "-m", "venv", VENV_DIR],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            fail(
                f"Failed to create virtual environment:\n{result.stderr.strip()}\n\n"
                "   On Solus try:  sudo eopkg install python3-devel"
            )
        ok(f"Virtual environment created at {VENV_DIR}")

    # Path to the venv's python
    venv_python = os.path.join(VENV_DIR, "bin", "python3")
    if not os.path.isfile(venv_python):
        venv_python = os.path.join(VENV_DIR, "bin", "python")

    if not has_pip(venv_python):
        fail(
            "pip is still missing inside the venv — this is unexpected.\n"
            "   Try bootstrapping manually:\n"
            "   curl https://bootstrap.pypa.io/get-pip.py | python3"
        )

    ok("pip is available inside the virtual environment")
    return venv_python


# ── 3. Install requirements ───────────────────────────────────────────────────
def install_requirements(python_exe):
    req_file = os.path.join(PROJECT_DIR, "requirements.txt")
    if not os.path.exists(req_file):
        fail("requirements.txt not found. Run install.py from the project folder.")

    step("Installing dependencies from requirements.txt...")

    with open(req_file) as f:
        packages = [l.strip() for l in f if l.strip() and not l.startswith("#")]

    all_ok = True
    for pkg in packages:
        name = pkg.split("==")[0]
        print(f"   {GRAY}Installing {pkg}...{RESET}", end=" ", flush=True)
        result = subprocess.run(
            [python_exe, "-m", "pip", "install", pkg, "--quiet"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"{GREEN}✔{RESET}")
        else:
            print(f"{RED}✘{RESET}")
            warn(f"Failed to install {name}:\n   {result.stderr.strip()}")
            all_ok = False

    if all_ok:
        ok("All dependencies installed")
    else:
        fail("Some packages failed to install. See warnings above.")


# ── 4. Verify imports ─────────────────────────────────────────────────────────
def verify_imports(python_exe):
    step("Verifying imports...")
    checks = {
        "requests":           "requests",
        "beautifulsoup4":     "bs4",
        "matplotlib":         "matplotlib",
        "tkinter (built-in)": "tkinter",
    }
    for display, mod in checks.items():
        result = subprocess.run(
            [python_exe, "-c", f"import {mod}"],
            capture_output=True
        )
        if result.returncode == 0:
            ok(display)
        else:
            fail(
                f"{display} could not be imported.\n"
                f"   Try manually: {python_exe} -m pip install {display}"
            )


# ── 5. Make main.py executable ────────────────────────────────────────────────
def make_executable():
    main_py = os.path.join(PROJECT_DIR, "main.py")
    if os.path.exists(main_py) and platform.system() == "Linux":
        os.chmod(main_py, 0o755)
        ok("main.py marked as executable")


# ── 6. Desktop launcher ───────────────────────────────────────────────────────
def create_desktop_launcher(python_exe):
    if platform.system() != "Linux":
        warn("Desktop launcher only supported on Linux — skipping")
        return

    step("Creating desktop launcher...")

    main_py     = os.path.join(PROJECT_DIR, "main.py")
    desktop_dir = os.path.expanduser("~/Desktop")
    apps_dir    = os.path.expanduser("~/.local/share/applications")

    # Always point the launcher at whichever python has the deps installed
    desktop_content = f"""[Desktop Entry]
Type=Application
Version=1.0
Name=Gold Price Tracker
GenericName=Gold Price Tracker
Comment=Live gold prices for Chennai — Times of India
Exec={python_exe} {main_py}
Icon=utilities-finance
Terminal=false
Categories=Finance;Utility;
StartupNotify=true
"""

    os.makedirs(apps_dir, exist_ok=True)
    for target_dir, label in [(apps_dir, "App menu"), (desktop_dir, "Desktop")]:
        if not os.path.isdir(target_dir):
            warn(f"{target_dir} not found — skipping {label} shortcut")
            continue
        path = os.path.join(target_dir, "gold_tracker.desktop")
        with open(path, "w") as f:
            f.write(desktop_content)
        os.chmod(path, 0o755)
        ok(f"{label} shortcut: {path}")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    banner()
    check_python()
    python_exe = ensure_pip_available()   # may create .venv/
    install_requirements(python_exe)
    verify_imports(python_exe)
    make_executable()
    create_desktop_launcher(python_exe)

    using_venv = python_exe.startswith(VENV_DIR)
    run_cmd = f"{python_exe} main.py" if using_venv else "python3 main.py"

    print(f"""
{GOLD}{BOLD}══════════════════════════════════════════{RESET}
{GREEN}{BOLD}  ✅  Installation complete!{RESET}

  Run the app:
    {BOLD}{run_cmd}{RESET}

  Or double-click {BOLD}gold_tracker.desktop{RESET} on your Desktop.
{GOLD}{BOLD}══════════════════════════════════════════{RESET}
""")


if __name__ == "__main__":
    main()
