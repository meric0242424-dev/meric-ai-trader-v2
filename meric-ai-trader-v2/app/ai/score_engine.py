from app.ai.indicators import closes, vols, ema, rsi, macd, bollinger, atr

class AIScoreEngine:
    """Kural tabanlı AI-score v2. Gerçek ML değil; üretime güvenli açıklanabilir skor motoru."""
    def analyze(self, symbol: str, k15, k1h, k4h, funding: float = 0.0, oi: float = 0.0) -> dict:
        c15, c1h, c4h = closes(k15), closes(k1h), closes(k4h)
        price = c15[-1]
        bull = bear = 0
        reasons=[]

        # Trend score
        if ema(c1h,21) > ema(c1h,55) and ema(c4h,21) > ema(c4h,55): bull += 25; reasons.append("MTF trend bullish")
        if ema(c1h,21) < ema(c1h,55) and ema(c4h,21) < ema(c4h,55): bear += 25; reasons.append("MTF trend bearish")
        if price > ema(c15,21) > ema(c15,55): bull += 15
        if price < ema(c15,21) < ema(c15,55): bear += 15

        # Momentum
        r15, r1h = rsi(c15), rsi(c1h)
        if 52 <= r15 <= 68 and r1h > 50: bull += 18; reasons.append("RSI momentum long")
        if 32 <= r15 <= 48 and r1h < 50: bear += 18; reasons.append("RSI momentum short")
        if macd(c15) > 0 and macd(c1h) > 0: bull += 12
        if macd(c15) < 0 and macd(c1h) < 0: bear += 12

        # Volatility / BB location
        lower, mid, upper = bollinger(c15)
        bb_pct=(price-lower)/(upper-lower) if upper>lower else .5
        if 0.35 < bb_pct < 0.75 and bull > bear: bull += 8
        if 0.25 < bb_pct < 0.65 and bear > bull: bear += 8
        atr_pct = atr(k15) / price * 100 if price else 0
        volatility_ok = 0.15 <= atr_pct <= 4.5

        # Volume
        v=vols(k15); avg=sum(v[-20:])/20 if len(v)>=20 else max(sum(v)/len(v),1)
        vol_ratio=v[-1]/avg if avg else 1
        if vol_ratio > 1.4:
            if c15[-1] > c15[-2]: bull += 10; reasons.append("hacim long teyidi")
            else: bear += 10; reasons.append("hacim short teyidi")

        # Funding crowd filter
        if funding > 0.0008: bull -= 10; bear += 5; reasons.append("funding long kalabalık")
        if funding < -0.0008: bear -= 10; bull += 5; reasons.append("funding short kalabalık")

        bull=max(0,bull); bear=max(0,bear); total=bull+bear
        score = int(round(max(bull,bear)/total*100)) if total else 50
        direction = "LONG" if bull>bear and score>=60 else "SHORT" if bear>bull and score>=60 else "NEUTRAL"
        if not volatility_ok:
            direction="NEUTRAL"; reasons.append("volatilite filtresi")

        sl_pct=max(0.5, min(3.0, atr_pct*1.4)) / 100
        tp_pct=sl_pct*1.8
        if direction == "LONG":
            sl=price*(1-sl_pct); tp=price*(1+tp_pct)
        elif direction == "SHORT":
            sl=price*(1+sl_pct); tp=price*(1-tp_pct)
        else:
            sl=tp=price

        return {"symbol":symbol,"direction":direction,"score":score,"bull":bull,"bear":bear,"price":price,"sl":round(sl,8),"tp":round(tp,8),"rsi15":r15,"rsi1h":r1h,"atr_pct":round(atr_pct,3),"vol_ratio":round(vol_ratio,2),"funding":funding,"open_interest":oi,"reasons":reasons[:8]}
