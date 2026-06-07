from src.line_webhook import split_line_messages
from src.response_generator import ResponseGenerator


def test_split_line_messages_keeps_short_message():
    assert split_line_messages("hello") == ["hello"]


def test_split_line_messages_splits_long_message():
    chunks = split_line_messages("a\n" * 5000, limit=1000)
    assert len(chunks) > 1
    assert all(len(chunk) <= 1000 for chunk in chunks)


def test_help_menu_lists_commands():
    text = ResponseGenerator.help_menu()
    assert "NVDA" in text
    assert "Watchlist" in text
    assert "Price alert" in text
