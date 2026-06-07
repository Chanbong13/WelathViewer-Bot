from src.intent_parser import IntentParser
from src.ticker_resolver import TickerResolver


def test_resolve_company_alias():
    parsed = IntentParser().parse("Tesla")
    assert TickerResolver().resolve(parsed) == ["TSLA"]


def test_resolve_sector():
    parsed = IntentParser().parse("หุ้น AI ตัวไหนน่าดู")
    assert "NVDA" in TickerResolver().resolve(parsed)
