from src.intent_parser import IntentParser


def test_parse_plain_ticker_defaults_to_scan():
    parsed = IntentParser().parse("NVDA")
    assert parsed.intent == "stock_detail_scan"
    assert parsed.tickers == ["NVDA"]


def test_parse_technical_thai():
    parsed = IntentParser().parse("ขอแนวรับแนวต้าน AAPL")
    assert parsed.intent == "technical_analysis"
    assert parsed.tickers == ["AAPL"]


def test_parse_compare():
    parsed = IntentParser().parse("เทียบ NVDA กับ AMD")
    assert parsed.intent == "peer_comparison"
    assert parsed.tickers == ["NVDA", "AMD"]


def test_parse_sector_scan():
    parsed = IntentParser().parse("สแกนหุ้น semiconductor")
    assert parsed.intent == "sector_scan"
    assert parsed.sector == "semiconductor"


def test_parse_help_command():
    parsed = IntentParser().parse("help")
    assert parsed.intent == "help"
