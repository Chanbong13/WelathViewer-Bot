from __future__ import annotations

import base64
import datetime as dt
import hashlib
import hmac
import json

import requests
from flask import Flask, Response, request

from config import Settings
from src.alert_manager import AlertManager
from src.daily_report import DailyReportService
from src.database import Database
from src.google_drive_uploader import GoogleDriveUploader
from src.intent_parser import IntentParser
from src.response_generator import ResponseGenerator
from src.stock_data import StockDataClient
from src.ticker_resolver import TickerResolver
from src.watchlist_manager import WatchlistManager


LINE_REPLY_ENDPOINT = "https://api.line.me/v2/bot/message/reply"


def create_app(settings: Settings) -> Flask:
    app = Flask(__name__)
    db = Database(settings.database_url)
    parser = IntentParser()
    resolver = TickerResolver()
    responses = ResponseGenerator(StockDataClient())
    watchlists = WatchlistManager(db)
    alerts = AlertManager(db)

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok", "runtime": "cloud-run-ready"}

    @app.post("/line/webhook")
    def line_webhook() -> Response:
        return _handle_line_webhook(settings, parser, resolver, responses, watchlists, alerts)

    @app.post("/webhook")
    def webhook() -> Response:
        return _handle_line_webhook(settings, parser, resolver, responses, watchlists, alerts)

    @app.post("/daily-report")
    def daily_report() -> tuple[dict, int]:
        if not _valid_daily_report_token(settings, request.headers.get("Authorization", ""), request.headers.get("X-Daily-Report-Token", "")):
            return {"error": "unauthorized"}, 401

        payload = request.get_json(force=True, silent=True) or {}
        report_date = payload.get("date")
        service = DailyReportService(settings, responses)
        result = service.generate(_parse_date(report_date) if report_date else None)
        upload_links = {}
        uploader = GoogleDriveUploader(settings)
        if uploader.is_configured:
            upload_links = uploader.upload_files(result["files"])
        return {
            "status": "ok",
            "date": result["date"],
            "summary": result["summary"],
            "files": [path.name for path in result["files"]],
            "drive_links": upload_links,
            "notebooklm_ready": True,
        }, 200

    return app


def _handle_line_webhook(
    settings: Settings,
    parser: IntentParser,
    resolver: TickerResolver,
    responses: ResponseGenerator,
    watchlists: WatchlistManager,
    alerts: AlertManager,
) -> Response:
    raw_body = request.get_data()
    if settings.line_channel_secret and not _valid_signature(settings.line_channel_secret, raw_body, request.headers.get("X-Line-Signature", "")):
        return Response("invalid signature", status=403)

    payload = request.get_json(force=True, silent=True) or {}
    for event in payload.get("events", []):
        if event.get("type") != "message" or event.get("message", {}).get("type") != "text":
            continue
        text = event["message"]["text"]
        user_id = event.get("source", {}).get("userId", "anonymous")
        reply_token = event.get("replyToken")
        message = handle_user_message(text, user_id, parser, resolver, responses, watchlists, alerts)
        if reply_token:
            _reply(settings, reply_token, split_line_messages(message))
    return Response("ok", status=200)


def handle_user_message(
    text: str,
    user_id: str,
    parser: IntentParser,
    resolver: TickerResolver,
    responses: ResponseGenerator,
    watchlists: WatchlistManager,
    alerts: AlertManager,
) -> str:
    parsed = parser.parse(text)
    tickers = resolver.resolve(parsed)

    if parsed.intent == "help":
        return responses.help_menu()
    if parsed.intent == "watchlist_summary":
        return watchlists.summary(user_id)
    if parsed.intent == "watchlist_add" and tickers:
        snapshot = responses.data_client.get_snapshot(tickers[0])
        return watchlists.add(user_id, tickers[0], snapshot.company_name, snapshot.sector)
    if parsed.intent == "watchlist_remove" and tickers:
        return watchlists.remove(user_id, tickers[0])
    if parsed.intent == "price_alert" and tickers:
        return alerts.create_from_text(user_id, tickers[0], text)
    if parsed.intent == "sector_scan" and parsed.sector:
        return responses.sector_scan(parsed.sector)
    if parsed.intent == "peer_comparison" and len(tickers) >= 2:
        return responses.compare(tickers)
    if not tickers:
        return "ยังไม่เจอข้อมูลหุ้นตัวนี้ครับ ลองส่งเป็น ticker เช่น NVDA, AAPL, TSLA หรือ MSFT อีกครั้งได้เลยครับ"
    if parsed.intent == "technical_analysis":
        return responses.technical_scan(tickers[0])
    if parsed.intent == "news_scan":
        return responses.news_scan(tickers[0])
    if parsed.intent == "fundamental_analysis":
        return responses.fundamental_scan(tickers[0])
    return responses.stock_scan(tickers[0])


def split_line_messages(message: str, limit: int = 4500) -> list[str]:
    if len(message) <= limit:
        return [message]
    chunks = []
    current = []
    size = 0
    for line in message.splitlines():
        if size + len(line) + 1 > limit and current:
            chunks.append("\n".join(current))
            current = []
            size = 0
        current.append(line)
        size += len(line) + 1
    if current:
        chunks.append("\n".join(current))
    return chunks[:5]


def _reply(settings: Settings, reply_token: str, messages: list[str]) -> None:
    if not settings.line_channel_access_token:
        return
    payload = {"replyToken": reply_token, "messages": [{"type": "text", "text": text[:5000]} for text in messages]}
    requests.post(
        LINE_REPLY_ENDPOINT,
        headers={"Authorization": f"Bearer {settings.line_channel_access_token}", "Content-Type": "application/json"},
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        timeout=20,
    ).raise_for_status()


def _valid_signature(secret: str, body: bytes, signature: str) -> bool:
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).digest()
    expected = base64.b64encode(digest).decode("utf-8")
    return hmac.compare_digest(expected, signature)


def _valid_daily_report_token(settings: Settings, authorization: str, header_token: str) -> bool:
    if not settings.daily_report_token:
        return True
    expected = settings.daily_report_token
    bearer = authorization.replace("Bearer ", "", 1).strip() if authorization.startswith("Bearer ") else ""
    return hmac.compare_digest(expected, header_token) or hmac.compare_digest(expected, bearer)


def _parse_date(value: str) -> dt.date:
    return dt.date.fromisoformat(value)
