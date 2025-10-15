# DimeDrop 🏀💸

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

Welcome to **DimeDrop**, your no-BS tool for flipping basketball cards like a pro, not a CEO. Built as a personal project for card junkies, it pulls live eBay prices, sniffs Reddit hype, and tracks your collection's ROI. Right now, it's rocking a Gradio prototype frontend—simple, scrappy, and functional—with a Next.js upgrade on the horizon. Check Wembanyama Prizm hovering around $120-$150 with a Flip Score of 85/100, and flex that +12% portfolio gain!

## 🎯 What's DimeDrop?

DimeDrop is an open-source sidekick for basketball card flippers. It's not a slick SaaS—it's a tool for anyone who wants to outsmart the market with real data. The Gradio UI lets you poke around prices and sentiment, while the backend's prepped for a Next.js leap when we're ready.

### 💰 Current Features (October 2025)

- **Price Tracking**: Grabs live eBay prices for cards you search or add. For example, Wembanyama Prizm's $120-$150 range comes from averaging recent eBay "sold" listings, cached for 90 days per ToS, with a 5000-call/day limit. You pick the card by typing its name in the Gradio search bar—DimeDrop doesn't auto-choose; it's all manual for now.
- **Sentiment Analysis**: Scans r/basketballcards posts for a Flip Score (e.g., 85/100 for Wemby, based on 70% positive buzz). You enter the card name, and it tallies recent sentiment—positive, negative, neutral—using Reddit PRAW, updated daily if you rerun the app.
- **Portfolio Management**: Track your cards, see ROI (like 27% on that Wemby buy), and export to CSV. Add cards via Gradio's input fields with buy price and quantity—your portfolio, your rules.
- **Smart Alerts**: Get pinged when a card's price spikes (e.g., Wemby > $150). Set a target price in Gradio, and it checks eBay data on refresh.
- **Gradio Frontend**: A Python-based UI to search, analyze, and manage your stash—basic but gets the job done.
- **Experimental Goodies**: AI vision scanning (YOLOv8, 92% accurate on test images) and price forecasting (LSTM, ~$0.53 off but still glitchy). Upload a card photo or request a forecast in Gradio, but expect some bugs.

**Coming Soon**: A Next.js frontend with dark mode, Tailwind CSS, and a slick dashboard.

## 🛠️ Tech Stack

- **Frontend**: Gradio (Python-based, prototype vibes).
- **Backend**: FastAPI (async, <2s responses), Python 3.12+, Poetry.
- **APIs**: eBay SDK (real "sold" listings), Reddit PRAW (sentiment).
- **Database**: SQLite (local, stores your portfolio and cached prices).
- **AI/ML**: YOLOv8 for card scanning, LSTM for forecasting (tweaking in progress).
- **Testing**: pytest, aiming for 97% coverage.

## 🚀 Quick Start

Fire up DimeDrop in ~10 minutes. No corporate handbook needed.

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
   - Backend API: `http://localhost:8000/docs` (Swagger UI).
   - Mobile: Use `http://your-local-ip:7860` (e.g., `192.168.1.10:7860`).

## 📊 How to Use It

## 📸 Screenshots

Check out DimeDrop in action—upload your app screenshots to `assets/` for proof:
![DimeDrop Gradio Interface](assets/Screenshot%20from%202025-10-15%2017-43-20.png)
![DimeDrop Gradio Interface](assets/Screenshot%20from%202025-10-15%2017-43-20.png)

## 🧪 Testing

Keep it solid:

```bash
poetry run pytest
```

## 🗺️ Roadmap (Oct 2025 - Jan 2026)

- **Oct 20, 2025**: Lock down Gradio UI, fix LSTM tensor bugs.
- **Nov 15, 2025**: Roll out AI vision scanning (YOLOv8 + TrOCR) for uploads.
- **Dec 1, 2025**: Start Next.js frontend (dark theme, Tailwind, ShadCN).
- **Jan 31, 2026**: Add LeBron and Curry cards, basic auth, 95% test coverage.

## 🤝 Contributing

This is a card flipper's passion project—jump in! Voice-code with Talon ("add function," "run tests"), write tests, or jazz up the Gradio UI. Fork the repo, make a branch (`git checkout -b feature/sick-idea`), and PR it. Got a hot take? Open an issue with "enhancement." Star the repo if you're feeling the love.

## 📄 License

MIT—flip cards, not copyrights. Hack it, share it, own it.

## 📞 Contact

Hit me at [b0onzy/dimedrop](https://github.com/b0onzy/dimedrop). Built with ❤️ for card hustlers chasing the next big score.
