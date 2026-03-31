#!/bin/bash
set -e

echo "Running post-merge setup..."

# Install frontend dependencies
if [ -f "frontend/package.json" ]; then
  echo "Installing frontend dependencies..."
  cd frontend && npm install --legacy-peer-deps && cd ..
fi

# Install backend dependencies
if [ -f "pyproject.toml" ]; then
  echo "Installing backend dependencies..."
  uv sync 2>/dev/null || pip install -e . --quiet 2>/dev/null || true
fi

echo "Post-merge setup complete."
