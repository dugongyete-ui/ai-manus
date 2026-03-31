#!/bin/bash
set -e

echo "========================================"
echo "  Auto Install - AI Manus Project"
echo "========================================"

# ── Backend Python Dependencies ───────────────────────────────────────────────
echo ""
echo "[1/4] Checking backend Python dependencies..."

BACKEND_PACKAGES=(
  "async-lru"
  "beanie"
  "beautifulsoup4"
  "curl-cffi"
  "cryptography"
  "debugpy"
  "docker"
  "e2b"
  "e2b-desktop"
  "fastapi"
  "httpx"
  "langchain"
  "langchain-anthropic"
  "langchain-community"
  "langchain-deepseek"
  "langchain-ollama"
  "langchain-openai"
  "markdownify"
  "mcp"
  "openai"
  "anthropic"
  "browser-use"
  "playwright"
  "pydantic"
  "pydantic-settings"
  "pyjwt"
  "pymongo"
  "python-dotenv"
  "python-multipart"
  "redis"
  "rich"
  "tavily-python"
  "sse-starlette"
  "uvicorn"
  "websockets"
  "pillow"
)

# Get list of already-installed packages (fast, no network)
INSTALLED=$(pip list --format=columns 2>/dev/null | awk 'NR>2 {print tolower($1)}')

MISSING=()
for pkg in "${BACKEND_PACKAGES[@]}"; do
  pkg_lower=$(echo "$pkg" | tr '[:upper:]' '[:lower:]' | tr '_' '-')
  if ! echo "$INSTALLED" | grep -qx "$pkg_lower"; then
    MISSING+=("$pkg")
  fi
done

if [ ${#MISSING[@]} -eq 0 ]; then
  echo "  All backend packages already installed."
else
  echo "  Installing missing: ${MISSING[*]}"
  pip install --quiet --disable-pip-version-check "${MISSING[@]}"
  echo "  Done."
fi

# ── Playwright Browsers ───────────────────────────────────────────────────────
echo ""
echo "[2/4] Checking Playwright browsers..."
if python3 -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); p.stop()" 2>/dev/null; then
  echo "  Playwright browsers already available."
else
  echo "  Installing Playwright Chromium browser..."
  python3 -m playwright install chromium 2>/dev/null || \
    echo "  Warning: Playwright browser install failed (sandbox env may not need local browsers)."
fi

# ── Frontend npm Dependencies ─────────────────────────────────────────────────
echo ""
echo "[3/4] Installing frontend npm dependencies..."
cd frontend
if [ -d "node_modules" ] && [ "$(ls -A node_modules 2>/dev/null)" ]; then
  echo "  node_modules exists, running npm install to sync any changes..."
fi
npm install --legacy-peer-deps --silent
cd ..
echo "  Frontend dependencies ready."

# ── Verify All Critical Imports ───────────────────────────────────────────────
echo ""
echo "[4/4] Verifying all critical Python imports..."

python3 - <<'PYEOF'
import importlib, sys

checks = [
    ("fastapi",            "fastapi"),
    ("uvicorn",            "uvicorn"),
    ("beanie",             "beanie"),
    ("pydantic",           "pydantic"),
    ("pydantic-settings",  "pydantic_settings"),
    ("langchain",          "langchain"),
    ("langchain-openai",   "langchain_openai"),
    ("langchain-anthropic","langchain_anthropic"),
    ("langchain-community","langchain_community"),
    ("langchain-deepseek", "langchain_deepseek"),
    ("langchain-ollama",   "langchain_ollama"),
    ("redis",              "redis"),
    ("pymongo",            "pymongo"),
    ("playwright",         "playwright"),
    ("browser-use",        "browser_use"),
    ("docker",             "docker"),
    ("e2b",                "e2b"),
    ("e2b-desktop",        "e2b_desktop"),
    ("tavily-python",      "tavily"),
    ("httpx",              "httpx"),
    ("mcp",                "mcp"),
    ("sse-starlette",      "sse_starlette"),
    ("markdownify",        "markdownify"),
    ("curl-cffi",          "curl_cffi"),
    ("beautifulsoup4",     "bs4"),
    ("pyjwt",              "jwt"),
    ("rich",               "rich"),
    ("python-dotenv",      "dotenv"),
    ("cryptography",       "cryptography"),
]

missing = []
for label, mod in checks:
    try:
        importlib.import_module(mod)
    except ImportError:
        missing.append(label)

if missing:
    print(f"  WARNING - Still missing: {missing}")
    sys.exit(1)
else:
    print(f"  All {len(checks)} packages verified OK!")
PYEOF

echo ""
echo "========================================"
echo "  Installation Complete! Everything OK."
echo "========================================"
echo ""
echo "Start the project:"
echo "  Backend : cd backend && python3 -m uvicorn app.main:app --host localhost --port 8000 --reload"
echo "  Frontend: cd frontend && npm run dev"
