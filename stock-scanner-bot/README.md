# Stock Scanner Bot

LINE chatbot / web chatbot for scanning stocks from Thai, English, and mixed-language user messages. The bot detects intent, resolves tickers or company names, fetches market data and news, calculates technical indicators, summarizes fundamentals and risks, scores the stock, and returns a structured educational analysis.

Every response includes a disclaimer. The bot does not provide guaranteed financial advice.

## Features

- LINE Messaging API webhook at `/line/webhook`
- Natural-language intent detection for Thai / English / mixed messages
- Ticker, company name, and sector resolution
- Stock detail scan
- Technical analysis scan
- News scan
- Fundamental analysis scan
- Peer comparison
- Sector scan
- User watchlist
- Price alert storage
- SQLite database by default
- LINE-safe long-message splitting
- Optional image card generator module

## Project Structure

```text
stock-scanner-bot/
  README.md
  requirements.txt
  .env.example
  main.py
  config.py

  src/
    line_webhook.py
    intent_parser.py
    ticker_resolver.py
    stock_data.py
    news_collector.py
    technical_analysis.py
    fundamental_analysis.py
    sentiment_analysis.py
    stock_scorer.py
    watchlist_manager.py
    alert_manager.py
    response_generator.py
    image_card_generator.py
    database.py

  tests/
    test_intent_parser.py
    test_ticker_resolver.py
    test_technical_analysis.py
    test_response_generator.py
```

## Install

```powershell
cd "C:\Users\Chanasorn T\OneDrive\เอกสาร\Money\stock-scanner-bot"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

On this machine, if `python` is not on PATH, use the bundled interpreter:

```powershell
& "C:\Users\Chanasorn T\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" main.py
```

## Environment Variables

```env
FINNHUB_API_KEY=
ALPHA_VANTAGE_API_KEY=
POLYGON_API_KEY=
NEWS_API_KEY=
LINE_CHANNEL_ACCESS_TOKEN=
LINE_CHANNEL_SECRET=
DATABASE_URL=sqlite:///data/stock_scanner.db
OPENAI_API_KEY=
APP_HOST=0.0.0.0
APP_PORT=8000
DEFAULT_LANGUAGE=th
MAX_NEWS_ITEMS=5
PRICE_HISTORY_PERIOD=1y
```

The current implementation works with Yahoo Finance via `yfinance` and RSS feeds. Finnhub, Alpha Vantage, Polygon, NewsAPI, and OpenAI keys are reserved for extending data quality and AI summarization.

## Set Up LINE Messaging API

1. Open [LINE Developers Console](https://developers.line.biz/console/).
2. Select your provider and Messaging API channel.
3. Copy `Channel access token` into:

```env
LINE_CHANNEL_ACCESS_TOKEN=
```

4. Copy `Channel secret` into:

```env
LINE_CHANNEL_SECRET=
```

5. Deploy this app to an HTTPS URL.
6. Set webhook URL:

```text
https://your-domain.com/line/webhook
```

7. Enable `Use webhook`.
8. Send a test message such as `NVDA`.

## Run Locally

```powershell
python main.py
```

Health check:

```text
http://localhost:8000/health
```

For LINE local webhook testing, expose your local server:

```powershell
ngrok http 8000
```

Then use:

```text
https://your-ngrok-domain.ngrok-free.app/line/webhook
```

## Deploy

Good deployment targets:

- Render
- Railway
- Fly.io
- VPS with nginx + systemd
- Google Cloud Run

Example production command:

```bash
gunicorn main:app --bind 0.0.0.0:$PORT
```

If using Render/Railway, set the environment variables in the hosting dashboard and set the start command to the command above.

### Render Blueprint

This repo includes:

```text
Procfile
runtime.txt
render.yaml
```

Render setup:

1. Push this repository to GitHub.
2. In Render, choose `New` -> `Blueprint`.
3. Select the repository.
4. Render will read `stock-scanner-bot/render.yaml`.
5. Add secret environment variables:

```env
LINE_CHANNEL_ACCESS_TOKEN=
LINE_CHANNEL_SECRET=
```

6. Deploy.
7. Use this webhook URL in LINE Developers:

```text
https://stock-scanner-bot.onrender.com/line/webhook
```

Replace the domain with the actual Render service URL.

## Supported Messages

```text
NVDA
วิเคราะห์ Tesla ให้หน่อย
ขอแนวรับแนวต้าน AAPL
หุ้น AI ตัวไหนน่าสนใจวันนี้
สแกนหุ้นกลุ่ม semiconductor
เทียบ AVGO กับ NVDA
ขอข่าว PLTR วันนี้
เพิ่ม NVDA เข้า watchlist
ลบ TSLA
สรุป watchlist
แจ้งเตือนถ้า NVDA ลงถึง 120
```

## Intents

- `stock_detail_scan`
- `technical_analysis`
- `news_scan`
- `fundamental_analysis`
- `peer_comparison`
- `sector_scan`
- `watchlist_add`
- `watchlist_remove`
- `watchlist_summary`
- `price_alert`

## Stock Scoring

Overall score uses:

```text
Fundamental score: 35%
Technical score: 30%
News sentiment score: 20%
Valuation score: 10%
Risk score: 5%
```

Labels:

```text
80-100 = Strong candidate
65-79 = Good but wait for price
50-64 = Neutral / Watch
35-49 = Weak
0-34 = Avoid
```

Customize scoring in:

[src/stock_scorer.py](<src/stock_scorer.py>)

## Add More Data Sources

Extend:

- [src/stock_data.py](<src/stock_data.py>) for market data APIs
- [src/news_collector.py](<src/news_collector.py>) for news APIs and investor relations pages
- [src/fundamental_analysis.py](<src/fundamental_analysis.py>) for SEC filings or financial statements
- [src/sentiment_analysis.py](<src/sentiment_analysis.py>) for AI sentiment models

## Connect With Google Drive And NotebookLM Later

This bot is designed to complement the existing daily briefing system. Later extensions can:

- Save each scan as Markdown
- Upload scan summaries to Google Drive
- Build NotebookLM source packets by ticker or sector
- Append ticker scans to daily NotebookLM source files

The NotebookLM source formatter already exists in the sibling `stock-briefing-agent` project and can be reused.

## Error Handling

The bot handles:

- Invalid ticker
- Company name not found
- Missing API keys
- Data source unavailable
- No recent news
- Long LINE response splitting
- Invalid LINE signature

Fallback response:

```text
ยังไม่เจอข้อมูลหุ้นตัวนี้ครับ ลองส่งเป็น ticker เช่น NVDA, AAPL, TSLA หรือ MSFT อีกครั้งได้เลยครับ
```

## Safety

Every analysis must include:

```text
หมายเหตุ: ข้อมูลนี้ใช้เพื่อการศึกษาและช่วยประกอบการตัดสินใจเท่านั้น ไม่ใช่คำแนะนำการลงทุนแบบรับประกันผลตอบแทน ผู้ลงทุนควรศึกษาข้อมูลเพิ่มเติมและบริหารความเสี่ยงด้วยตนเอง
```
