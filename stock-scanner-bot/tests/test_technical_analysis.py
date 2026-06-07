import pandas as pd

from src.technical_analysis import TechnicalAnalysis


def test_technical_analysis_basic_metrics():
    frame = pd.DataFrame(
        {
            "Close": list(range(1, 260)),
            "High": list(range(2, 261)),
            "Low": list(range(0, 259)),
            "Volume": [1000] * 259,
        }
    )
    result = TechnicalAnalysis().analyze(frame)
    assert result["ma20"] is not None
    assert result["ma50"] is not None
    assert result["ma200"] is not None
    assert result["trend"] == "Strong uptrend"
