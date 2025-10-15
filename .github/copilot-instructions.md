# DimeDrop AI Agent Instructions

## Overview

DimeDrop is a basketball card flipping platform with Gradio frontend and FastAPI backend. Tracks eBay prices, Reddit sentiment, manages portfolios, and uses AI for card scanning/forecasting.

## Architecture

- **Frontend**: Gradio app (`app.py`) with modular components in `components/` (e.g., `PriceTrackerComponent` calls backend APIs).
- **Backend**: FastAPI (`Backend/backend/main.py`) with core services in `backend/app/core/` (price_tracker, sentiment_analyzer, portfolio_tracker, etc.).
- **Data Flow**: Frontend → Backend APIs → External APIs (eBay/Reddit) → SQLite cache (via `database.py`).
- **Why**: Modular for scalability; Gradio for rapid prototyping, FastAPI for async performance; 90-day eBay cache per ToS.

## Key Components

- `price_tracker.py`: eBay SDK fetches prices, caches in SQLite.
- `sentiment_analyzer.py`: PRAW analyzes Reddit r/basketballcards for Flip Scores.
- `portfolio_tracker.py`: Tracks buys/sells, calculates ROI.
- `vision_processor.py`: YOLOv8 scans card images.
- `forecast_model.py`: LSTM predicts prices (experimental).

## Workflows

- **Setup**: `poetry install` in `Backend/`, copy `.env.example` to `.env`, add eBay/Reddit keys.
- **Run Backend**: `./Backend/run.sh` (uvicorn --reload --host 0.0.0.0 --port 8000).
- **Run Frontend**: `python app.py` (Gradio on localhost:7860).
- **Test**: `pytest` in `Backend/backend/tests/` (async tests with pytest-asyncio).
- **Debug**: Check logs in terminal; API docs at /docs.

## Conventions

- **Deps**: Poetry-managed (`pyproject.toml`); dev deps include pytest, black.
- **Auth**: JWT via Auth0 (`services/auth.py`); use `get_current_user` for protected routes.
- **DB**: SQLite via Supabase client (`database.py`); migrations auto-handled.
- **Imports**: Relative from backend root (e.g., `from backend.app.core.price_tracker import ...`).
- **Async**: All API endpoints async; use httpx for external calls.
- **Caching**: 90-day expiry for eBay data; check `CacheOperations` before API calls.

## Examples

- Add price endpoint: In `main.py`, import and include router (e.g., `from backend.app.api.ebay import router`).
- Test auth: Use fixtures in `test_auth.py` for JWT mocking.
- Component: Extend `components/price_tracking.py` for new UI features.</content>
  <parameter name="filePath">/home/boonzy/dev/opensource/my-projects/dimedrop/.github/copilot-instructions.md
