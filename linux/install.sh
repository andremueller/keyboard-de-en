#!/usr/bin/env bash
# Wrapper script: sets up Python venv and runs install.py
# Usage: ./linux/install.sh <command>
# Commands: check | prepare | install | update | uninstall | load

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
REQUIREMENTS="$SCRIPT_DIR/requirements.txt"
INSTALL_PY="$SCRIPT_DIR/install.py"
COMMAND="${1:-check}"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
info()  { echo "  [INFO]  $*"; }
ok()    { echo "  [ OK ]  $*"; }
warn()  { echo "  [WARN]  $*"; }
err()   { echo " [ERROR]  $*" >&2; }

# ---------------------------------------------------------------------------
# Ensure Python 3 is available
# ---------------------------------------------------------------------------
if ! command -v python3 &>/dev/null; then
    err "python3 not found. Please run 'make prepare' first."
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
info "Python $PYTHON_VERSION found."

# ---------------------------------------------------------------------------
# Create or update venv
# ---------------------------------------------------------------------------
if [ ! -d "$VENV_DIR" ]; then
    info "Creating Python virtual environment in $VENV_DIR ..."
    python3 -m venv "$VENV_DIR"
    ok "Virtual environment created."
fi

VENV_PYTHON="$VENV_DIR/bin/python"
VENV_PIP="$VENV_DIR/bin/pip"

# ---------------------------------------------------------------------------
# Install / update requirements
# ---------------------------------------------------------------------------
REQS_STAMP="$VENV_DIR/.requirements_installed"
if [ ! -f "$REQS_STAMP" ] || [ "$REQUIREMENTS" -nt "$REQS_STAMP" ]; then
    info "Installing Python dependencies from requirements.txt ..."
    "$VENV_PIP" install --quiet --upgrade pip
    # Try to install lxml; if it fails (e.g. missing libxml2 headers), continue
    if "$VENV_PIP" install --quiet -r "$REQUIREMENTS"; then
        ok "Python dependencies installed (lxml available)."
    else
        warn "lxml could not be installed – falling back to stdlib xml.etree.ElementTree."
        warn "XML formatting may be less pretty, but functionality is identical."
    fi
    touch "$REQS_STAMP"
fi

# ---------------------------------------------------------------------------
# Run install.py
# ---------------------------------------------------------------------------
exec "$VENV_PYTHON" "$INSTALL_PY" "$COMMAND"
