# AI Manus

## Overview
AI Manus adalah sistem AI Agent general-purpose yang mengeksekusi task menggunakan berbagai tools (Terminal, Browser, File, Web Search) di dalam sandbox environment terisolasi. Fitur utama: real-time task monitoring, user takeover capability, dan integrasi MCP tools.

## Tech Stack
- **Frontend:** Vue.js 3 + Vite + TypeScript + Tailwind CSS + Monaco Editor
- **Backend:** Python 3.12 + FastAPI + LangChain (OpenAI-compatible via Cloudflare AI Gateway)
- **Database:** MongoDB Atlas (cloud)
- **Cache/Queue:** Redis Cloud
- **Sandbox:** E2B Cloud Sandbox (menggantikan Docker)

## Project Structure
```
frontend/    # Vue.js 3 web application
backend/     # FastAPI backend server
sandbox/     # Kode internal sandbox (referensi, tidak digunakan langsung)
claw/        # OpenClaw integration (disabled)
mockserver/  # Mock API server untuk testing
docs/        # Dokumentasi arsitektur
```

## Workflows
- **Start application** — Frontend Vue.js dev server (`cd frontend && npm run dev`) di port 5000 (webview)
- **Backend API** — FastAPI backend (`cd backend && python3 -m uvicorn app.main:app --host localhost --port 8000 --reload`) di port 8000 (console)

## Konfigurasi (backend/.env)
- **LLM:** Cloudflare AI Gateway (OpenAI-compatible), model `workers-ai/@cf/meta/llama-3.3-70b-instruct-fp8-fast`
- **MongoDB:** MongoDB Atlas (cloud cluster)
- **Redis:** Redis Cloud
- **E2B:** E2B Cloud Sandbox untuk eksekusi task agent
- **Auth:** Local auth (`admin@example.com` / `admin123`)

## Perubahan dari Docker ke E2B Desktop
- Semua Dockerfile dihapus
- `docker_sandbox.py` digantikan oleh `backend/app/infrastructure/external/sandbox/e2b_sandbox.py`
- `dependencies.py` diupdate untuk menggunakan `E2BSandbox`
- `config.py` ditambah field `e2b_api_key`
- Claw feature dinonaktifkan (`CLAW_ENABLED=false`)
- Import `langchain_classic` diperbaiki ke `langchain` 1.x compatible
- `RetryWithErrorOutputParser` digantikan dengan implementasi retry custom

## E2B Desktop Sandbox (VNC Support)
- **Package:** `e2b-desktop==2.3.0` + `e2b==2.19.0`
- **Template:** Ubuntu 22.04 + XFCE desktop dengan noVNC streaming
- **VNC Flow:** `E2BDesktopSDK.create()` → `stream.start()` → `wss://{sandbox-id}-6080.e2b.dev/websockify`
- **CDP Flow:** Chrome di DISPLAY=:99 → CDP port 9222 → `http://{sandbox-id}-9222.e2b.dev`
- **Dual SDK pattern:** 
  - `e2b_desktop.Sandbox` (sync, thread pool) untuk desktop creation & VNC URL
  - `e2b.AsyncSandbox` (async) untuk file/command operations
- **Browser imports:** Lazy-loaded di `get_browser()` untuk hindari startup error jika `browser_use` tidak terinstall

## Akses Login
- Email: `admin@example.com`
- Password: `admin123`

## Catatan
- Backend menggunakan `localhost` sebagai host, frontend menggunakan `0.0.0.0`
- Frontend proxy `/api` → `http://localhost:8000`
- VNC view menggunakan noVNC (RFB protocol via WebSocket) yang sudah ada di frontend
- Backend VNC WebSocket proxy di `/sessions/{id}/vnc` meneruskan ke E2B Desktop noVNC
