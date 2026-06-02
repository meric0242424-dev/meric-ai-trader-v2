from app.ai.score_engine import AIScoreEngine

def fake_kline(price):
    return [0, price, price*1.01, price*0.99, price, 1000]

def test_score_engine_runs():
    k=[fake_kline(100+i*0.1) for i in range(160)]
    out=AIScoreEngine().analyze("BTCUSDT", k, k, k)
    assert "score" in out
    assert out["direction"] in ["LONG","SHORT","NEUTRAL"]
