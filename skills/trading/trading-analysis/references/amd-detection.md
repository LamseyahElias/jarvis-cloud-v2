# AMD (Accumulation, Manipulation, Distribution) Detection — XAUUSD

Condensed algorithmic reference for Smart Money Concepts AMD pattern detection on gold.

## Phase Definitions

### Accumulation
Institutional order building. Price consolidates in a tight range, volume drops, ATR compresses.

**Detection criteria:**
- ATR(14) < 75% of 50-period ATR average
- 10-candle range < 1.0% of current price
- Volume ratio (vol / 20-period MA) < 1.0x
- Candle bodies are small relative to range

**XAUUSD specifics:** Accumulation typically occurs during Asian session (00:00–08:00 UTC). Gold's Asian session ADR is ~$8-15, vs $25-40 during London/NY.

### Manipulation
Liquidity sweep — price breaks a key level to trigger stops, then reverses. The "trap" phase.

**Detection criteria:**
- Price breaks above range high OR below range low
- But closes back inside the range (false breakout)
- Wick-to-body ratio > 50% (rejection candle)
- Often coincides with session open (London 07:00 UTC, NY 13:00 UTC)

**Direction inference:**
- Broke HIGH but closed below → BEARISH manipulation (trapped longs, real move is down)
- Broke LOW but closed above → BULLISH manipulation (trapped shorts, real move is up)

**XAUUSD specifics:** London open manipulation is the most reliable. Gold frequently sweeps Asian session high/low in the first 30-60 minutes of London, then reverses. NY open produces a second manipulation window.

### Distribution
The real directional move. Institutions distribute their accumulated position as price trends.

**Detection criteria:**
- ATR(14) > 120% of 50-period average (volatility expansion)
- Volume ratio > 1.3x (volume expansion)
- Strong directional candles (large bodies, small wicks)
- EMA alignment confirms direction

**XAUUSD specifics:** Distribution on gold often produces $20-50 moves. The strongest moves occur during London-NY overlap (13:00–16:00 UTC).

## Confluence Scoring

Each signal adds weight. Minimum 3 independent confirmations before a trade recommendation.

| Signal | Weight | Bullish | Bearish |
|--------|--------|---------|---------|
| EMA 9/21/50 alignment | 2.0 | 9 > 21 > 50 | 9 < 21 < 50 |
| RSI momentum | 1.0 | RSI > 60 | RSI < 40 |
| MACD histogram | 1.0 | Positive | Negative |
| AMD phase | 1.5 | Bullish manipulation confirmed | Bearish manipulation confirmed |
| Volume expansion | 1.0 | Rising vol + bullish candle | Rising vol + bearish candle |

Score threshold: ≥3.5 for HIGH confidence, 2.0-3.5 for MEDIUM, <2.0 for LOW.

## Session Schedule (UTC)

| Session | UTC Hours | Typical XAUUSD Behavior |
|---------|-----------|------------------------|
| Asian | 00:00–08:00 | Range/accumulation, low vol ($8-15 range) |
| London Open | 07:00–08:00 | Manipulation phase — sweeps Asian range |
| London | 08:00–16:00 | Trend development / distribution |
| NY Open | 13:00–14:00 | Second manipulation window |
| London-NY Overlap | 13:00–16:00 | Highest volatility — distribution peak |
| NY Afternoon | 16:00–22:00 | Trend continuation or reversal |

## Key XAUUSD Levels to Watch

- **Round numbers**: $50 increments (e.g., $4500, $4550) act as psychological S/R
- **Previous Day High/Low (PDH/PDL)**: Primary liquidity pools for manipulation sweeps
- **Asian Range High/Low**: The most common manipulation targets during London open
- **Weekly Open**: Institutional reference level for weekly bias

## Risk Parameters (Gold-Specific)

- Typical daily ATR: $40-70 (varies with macro environment)
- Recommended SL: 1.0-1.5x ATR of entry timeframe
- Spread at ICMarkets: ~15-25 points ($0.15-0.25) during London/NY, widens during Asian/news
- Swap: Check MT5 for current rates — gold swaps are significant for multi-day holds
- News events that move gold: FOMC, NFP, CPI, PPI, GDP, geopolitical escalation
