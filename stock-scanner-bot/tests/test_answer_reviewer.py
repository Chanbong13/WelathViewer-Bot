from src.answer_reviewer import AnswerReviewer


def test_reviewer_revises_missing_disclaimer_and_risk():
    reviewer = AnswerReviewer()
    review = reviewer.review("NVDA", "Stock looks constructive.", has_stock_context=True)
    assert not review.review_passed
    revised = reviewer.revise("Stock looks constructive.", review)
    assert "Disclaimer" in revised
    assert "Risk" in revised
