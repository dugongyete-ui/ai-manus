# AI Manus

## Overview
AI Manus is a general-purpose AI Agent system that executes tasks using various tools (Terminal, Browser, File, Web Search) within isolated sandbox environments. It features real-time task monitoring, user takeover capability, and integration with external MCP tools.

## Tech Stack
- **Frontend:** Vue.js 3 + Vite + TypeScript + Tailwind CSS + Monaco Editor
- **Backend:** Python 3.12 + FastAPI + LangChain (OpenAI/Anthropic/DeepSeek/Ollama)
- **Database:** MongoDB (via Beanie ODM)
- **Cache/Queue:** Redis (Streams)
- **Sandbox:** Docker-based Ubuntu containers

## Project Structure
```
frontend/    # Vue.js 3 web application
backend/     # FastAPI backend server
sandbox/     # Code running inside Docker sandbox containers
claw/        # OpenClaw integration (per-user isolated AI assistants)
mockserver/  # Mock API server for testing
docs/        # Architecture and configuration docs
```

## Replit Setup
- **Frontend workflow:** `cd frontend && npm run dev` on port 5000 (webview)
- Frontend configured with `host: '0.0.0.0'`, `port: 5000`, `allowedHosts: true` to work with Replit proxy
- The full stack (backend + MongoDB + Redis + Docker sandboxes) requires Docker Compose and is not running in Replit dev mode

## Configuration
- Backend config via environment variables (see `.env.example`)
- Key services required for full functionality: MongoDB, Redis, Docker daemon
- Authentication modes: `password`, `none`, `local` (via `AUTH_PROVIDER` env var)
- LLM provider configured via `API_KEY`, `MODEL_NAME`, `MODEL_PROVIDER` env vars

## Deployment
- Configured as a static site deployment (builds frontend with `npm run build`)
- Full production deployment uses Docker Compose (see `docker-compose.yml`)
