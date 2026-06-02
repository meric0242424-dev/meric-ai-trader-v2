def closes(k): return [float(x[4]) for x in k]
def highs(k): return [float(x[2]) for x in k]
def lows(k): return [float(x[3]) for x in k]
def vols(k): return [float(x[5]) for x in k]

def ema(values, period):
    if not values: return 0.0
    if len(values) < period: return values[-1]
    k = 2 / (period + 1)
    out = sum(values[:period]) / period
    for v in values[period:]: out = v * k + out * (1-k)
    return out

def rsi(values, period=14):
    if len(values) < period + 1: return 50.0
    gains, losses = [], []
    for i in range(len(values)-period, len(values)):
        d = values[i] - values[i-1]
        gains.append(max(d, 0)); losses.append(max(-d, 0))
    ag=sum(gains)/period; al=sum(losses)/period
    if al == 0: return 100.0
    return round(100 - 100/(1+ag/al), 2)

def macd(values):
    return ema(values, 12) - ema(values, 26)

def bollinger(values, period=20, mult=2.0):
    v=values[-period:]
    m=sum(v)/len(v)
    std=(sum((x-m)**2 for x in v)/len(v))**0.5
    return m-mult*std, m, m+mult*std

def atr(k, period=14):
    if len(k) < period + 1: return 0.0
    trs=[]
    for i in range(1, len(k)):
        h,l,cprev=float(k[i][2]),float(k[i][3]),float(k[i-1][4])
        trs.append(max(h-l, abs(h-cprev), abs(l-cprev)))
    return sum(trs[-period:])/period
