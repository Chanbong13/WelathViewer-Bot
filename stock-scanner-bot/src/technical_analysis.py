from __future__ import annotations

import numpy as np
import pandas as pd


class TechnicalAnalysis:
    def analyze(self, history: pd.DataFrame) -> dict:
        if history.empty or "Close" not in history:
            return self.empty()
        close = history["Close"].dropna()
        high = history["High"].dropna() if "High" in history else close
        low = history["Low"].dropna() if "Low" in history else close
        volume = history["Volume"].dropna() if "Volume" in history else pd.Series(dtype=float)
        price = float(close.iloc[-1])
        ma20 = self._ma(close, 20)
        ma50 = self._ma(close, 50)
        ma200 = self._ma(close, 200)
        macd, signal = self._macd(close)
        bb_upper, bb_lower = self._bollinger(close)
        support = float(low.tail(30).min()) if len(low) else None
        resistance = float(high.tail(30).max()) if len(high) else None
        return {
            "price": round(price, 2),
            "ma20": self._round(ma20),
            "ma50": self._round(ma50),
            "ma200": self._round(ma200),
            "rsi14": self._round(self._rsi(close)),
            "macd": self._round(macd),
            "macd_signal": self._round(signal),
            "macd_interpretation": self._macd_view(macd, signal),
            "bollinger_upper": self._round(bb_upper),
            "bollinger_lower": self._round(bb_lower),
            "average_volume_20d": self._round(volume.tail(20).mean() if len(volume) else None),
            "volume_trend": self._volume_trend(volume),
            "support": self._round(support),
            "resistance": self._round(resistance),
            "recent_swing_high": self._round(float(high.tail(10).max()) if len(high) else None),
            "recent_swing_low": self._round(float(low.tail(10).min()) if len(low) else None),
            "year_high": self._round(float(high.tail(252).max()) if len(high) else None),
            "year_low": self._round(float(low.tail(252).min()) if len(low) else None),
            "buy_zone": self._zone(support, 1.01),
            "take_profit_zone": self._zone(resistance, 0.99),
            "stop_loss_area": self._zone(support, 0.97),
            "trend": self._trend(price, ma20, ma50, ma200),
            "momentum": self._momentum(self._rsi(close)),
        }

    @staticmethod
    def empty() -> dict:
        keys = ["price", "ma20", "ma50", "ma200", "rsi14", "macd", "macd_signal", "bollinger_upper", "bollinger_lower", "average_volume_20d", "support", "resistance", "recent_swing_high", "recent_swing_low", "year_high", "year_low", "buy_zone", "take_profit_zone", "stop_loss_area"]
        data = {key: None for key in keys}
        data.update({"volume_trend": "Unknown", "trend": "Unknown", "momentum": "Unknown", "macd_interpretation": "Unknown"})
        return data

    @staticmethod
    def _ma(close: pd.Series, window: int) -> float | None:
        return float(close.rolling(window).mean().iloc[-1]) if len(close) >= window else None

    @staticmethod
    def _rsi(close: pd.Series, period: int = 14) -> float | None:
        if len(close) <= period:
            return None
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(period).mean()
        loss = -delta.clip(upper=0).rolling(period).mean()
        rs = gain / loss.replace(0, np.nan)
        value = 100 - (100 / (1 + rs))
        return float(value.iloc[-1]) if not pd.isna(value.iloc[-1]) else None

    @staticmethod
    def _macd(close: pd.Series) -> tuple[float | None, float | None]:
        if len(close) < 35:
            return None, None
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()
        return float(macd.iloc[-1]), float(signal.iloc[-1])

    @staticmethod
    def _bollinger(close: pd.Series) -> tuple[float | None, float | None]:
        if len(close) < 20:
            return None, None
        mid = close.rolling(20).mean()
        std = close.rolling(20).std()
        return float((mid + 2 * std).iloc[-1]), float((mid - 2 * std).iloc[-1])

    @staticmethod
    def _trend(price: float, ma20: float | None, ma50: float | None, ma200: float | None) -> str:
        if ma20 and ma50 and ma200 and price > ma20 > ma50 > ma200:
            return "Strong uptrend"
        if ma20 and ma50 and price > ma20 > ma50:
            return "Uptrend"
        if ma20 and ma50 and price < ma20 < ma50:
            return "Weak / correction"
        if ma50 and price < ma50:
            return "Below MA50"
        return "Mixed"

    @staticmethod
    def _momentum(rsi: float | None) -> str:
        if rsi is None:
            return "Unknown"
        if rsi > 70:
            return "Overbought"
        if rsi < 30:
            return "Oversold"
        return "Neutral"

    @staticmethod
    def _macd_view(macd: float | None, signal: float | None) -> str:
        if macd is None or signal is None:
            return "Unknown"
        return "Bullish momentum" if macd > signal else "Bearish momentum"

    @staticmethod
    def _volume_trend(volume: pd.Series) -> str:
        if len(volume) < 30:
            return "Unknown"
        recent = volume.tail(5).mean()
        base = volume.tail(20).mean()
        if recent > base * 1.25:
            return "Rising"
        if recent < base * 0.75:
            return "Falling"
        return "Stable"

    @staticmethod
    def _zone(value: float | None, multiplier: float) -> float | None:
        return round(value * multiplier, 2) if value else None

    @staticmethod
    def _round(value) -> float | None:
        try:
            if value is None or pd.isna(value):
                return None
            return round(float(value), 2)
        except (TypeError, ValueError):
            return None
