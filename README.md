# DimeDrop 🏀💸

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

Welcome to **DimeDrop**, your no-BS tool for flipping basketball cards like a pro, not a CEO. Built as a personal project for card junkies, it tracks eBay prices, sniffs out Reddit hype, and keeps your collection's ROI in check. Right now, it's running on a Gradio prototype frontend (simple, effective, a bit scrappy), with a Next.js glow-up planned for the future. Catch that Wembanyama Prizm at ~$150 with a Flip Score of 85/100 and flex your +12% portfolio gains.

## 🎯 What's DimeDrop?

DimeDrop is an open-source sidekick for basketball card flippers. It's not a fancy SaaS—it's a tool for anyone who wants to outsmart the market with data. The Gradio frontend is bare-bones but gets the job done, while the backend's ready to scale when we hit the Next.js court.

### 💰 Current Features (October 2025)

- **Price Tracking**: Live eBay prices (e.g., Wembanyama Prizm at $150 avg, cached 90 days per ToS).
- **Sentiment Analysis**: Reddit's r/basketballcards vibe check (Flip Score 85/100 for Wemby, 70% positive buzz).
- **Portfolio Management**: Track your cards, see ROI (like 27% on that Wemby buy), and export to CSV for taxes.
- **Smart Alerts**: Get pinged when prices spike (e.g., Wemby > $150).
- **Gradio Frontend**: Simple Python UI to browse prices, check sentiment, and manage your stash.
- **Experimental Goodies**: AI vision scanning (YOLOv8) and price forecasting (LSTM, ~$0.53 accurate but still tweaking).

**Coming Soon**: A sleek Next.js frontend with dark mode, Tailwind CSS, and a proper dashboard.

## 🛠️ Tech Stack

- **Frontend**: Gradio (Python-based, prototype vibes).
- **Backend**: FastAPI (async, <2s responses), Python 3.12+, Poetry.
- **APIs**: eBay SDK (real data, per recent commit), Reddit PRAW (sentiment).
- **Database**: SQLite (local, lightweight). Supabase integration in the works.
- **AI/ML**: YOLOv8 for card scanning, LSTM for forecasting (buggy but promising).
- **Testing**: pytest, targeting 97% coverage (per `DEVELOPMENT.md`).

## 🚀 Quick Start

Get DimeDrop up in ~10 minutes. No suit-and-tie required.

### Prerequisites

- Python 3.12+ ([python.org](https://www.python.org/downloads/)).
- Poetry (`pip install poetry`).
- Git.
- API keys for eBay and Reddit (optional for basic use).

### Installation

1. **Clone the repo**:

   ```bash
   git clone https://github.com/b0onzy/dimedrop.git
   cd dimedrop
   ```

2. **Install dependencies**:

   ```bash
   poetry install
   ```

3. **Set up environment variables**:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your keys (just eBay and Reddit for now):

   ```bash
   # eBay API (get from developer.ebay.com)
   EBAY_APP_ID=your_ebay_app_id
   EBAY_CERT_ID=your_ebay_cert_id
   EBAY_DEV_ID=your_ebay_dev_id

   # Reddit API (get from reddit.com/prefs/apps)
   REDDIT_CLIENT_ID=your_reddit_client_id
   REDDIT_CLIENT_SECRET=your_reddit_client_secret
   REDDIT_USER_AGENT=DimeDrop:v1.0
   ```

4. **Run the app**:

   ```bash
   # Backend (FastAPI, new terminal)
   poetry run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

   # Frontend (Gradio, new terminal)
   poetry run python frontend/gradio_app.py
   ```

5. **Access the app**:
   - Gradio UI: `http://localhost:7860` (check terminal for port).
   - Backend API: `http://localhost:8000/docs` (Swagger UI for geeks).
   - Mobile: Use `http://your-local-ip:7860` (e.g., `192.168.1.10:7860`).

## 📊 How to Use It

- **Search Cards**: Type "Wembanyama Prizm" in Gradio to see eBay prices ($120-$150 range).
- **Check Sentiment**: Get the Flip Score (85/100 = Reddit's hyped).
- **Manage Portfolio**: Add cards, track buys, and check ROI.
- **Set Alerts**: Pinged when Wemby's price moons past $150.

## 📸 Screenshots

Here's DimeDrop in action—upload your app screenshots to `assets/` for visual proof:

![DimeDrop Gradio Interface](assets/Screenshot%20from%202025-10-15%2013-48-06.png)

## 🧪 Testing

Make sure it doesn't flop:

```bash
poetry run pytest
```

## 🗺️ Roadmap (Oct 2025 - Jan 2026)

- **Oct 20, 2025**: Stabilize Gradio UI, squash LSTM tensor bugs (per `CHANGELOG.md`).
- **Nov 15, 2025**: Add AI vision scanning (YOLOv8 + TrOCR) for card uploads.
- **Dec 1, 2025**: Kick off Next.js frontend (dark theme, Tailwind, ShadCN).
- **Jan 31, 2026**: Support LeBron and Curry cards, add basic auth, hit 95% test coverage.

## 🤝 Contributing

This is a card flipper's passion project, so dive in! Voice-code with Talon ("add function," "run tests"), write tests, or spruce up the Gradio UI. Fork the repo, make a branch (`git checkout -b feature/sick-idea`), and PR it. Got a hot take? Open an issue with "enhancement." Star the repo if you're feeling the love.

## 📄 License

MIT—flip cards, not copyrights. Hack it, share it, own it.

## 📞 Contact

Hit me at [b0onzy/dimedrop](https://github.com/b0onzy/dimedrop). Built with ❤️ for card hustlers chasing the next big score.
