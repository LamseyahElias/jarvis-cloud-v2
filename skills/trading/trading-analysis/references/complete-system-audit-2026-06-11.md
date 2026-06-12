# JARVIS Trading Engine — Complete System Audit
## 2026-06-11 13:36 UTC

This document contains the full audit output. It was produced on demand by the boss (Elias).

## How to Regenerate

The audit examines every script in `~/trading/scripts/`, the RPyC server at `/mnt/c/Users/USER/mt5_rpyc_server.py`, and the SQLite DB at `~/trading/data/trades.db`. It also runs `dry_test_reporter.py --verbose` for live stats.

```bash
# Quick regeneration
cd ~/trading/scripts
python3 dry_test_reporter.py --verbose

# Full file-by-file reading (from the session):
# 1. mt5_bridge.py — RPyC client with auto-retry
# 2. mt5_rpyc_server.py — Windows server exposing MT5
# 3. xauusd_analyzer.py — Technical analysis engine
# 4. data_provider.py — OHLCV data fetching
# 5. auto_scalper.py — Dry-mode signal generator
# 6. position_manager.py — Dry-mode signal evaluator
# 7. trade_db.py — SQLite ORM
# 8. trade_executor.py — Legacy, not used
# 9. xauusd_monitor.py — Legacy, not used
# 10. dry_test_reporter.py — Stats reporter
```

## Architecture Diagram

```
WSL (Linux)                         Windows
┌──────────────────┐                ┌──────────────────┐
│ auto_scalper.py   │                │ mt5_rpyc_server  │
│ (every 2m, cron)  │ ──RPyC v6──►  │ (0.0.0.0:18812)  │
│ position_mgr.py   │                │     │            │
│ (every 1m, cron)  │ ◄───────      │ MT5 Terminal     │
└──────┬────────────┘                └──────────────────┘
       │ writes
       ▼
┌──────────────┐
│ trade_db.py   │
│ (SQLite)      │
│ ~/trading/data│
│ /trades.db    │
└──────────────┘
```

## Key Findings (Summary)

| Category | Verdict |
|---|---|
| Architecture | Sound. Two-tier (WSL client + Windows server) is viable. |
| Data Flow | Clean and linear. MT5→analysis→score→DB. |
| Dry Test Framework | Functionally complete. 5 signals generated, 4 resolved. |
| Market Analysis | Superficial. No BOS/CHoCH, no news, no volatility filter. |
| Risk Management | CRITICALLY WEAK. No daily stop, no cooldown, no sizing model. |
| Execution Reliability | RPyC has intermittent None returns. Retry logic helps but adds latency. |
| Logging | Comprehensive schema but some fields always 0 (bars_held, balance_after). |
| Known Bugs | 7 confirmed bugs (see below). |

## Confirmed Bugs

| # | Bug | File | Line |
|---|---|---|---|
| 1 | Profit factor calculation broken: `max(gross_losses, 0.01)` when gross_losses is negative → division by near-zero (0.01) | `trade_db.py` get_stats() | ~line 164 |
| 2 | bars_held always 0: PM passes `bars_held=0` to `log_closed()` | `position_manager.py` | All log_closed calls |
| 3 | balance_after always 0: PM passes `balance_after=0, equity_after=0` | `position_manager.py` | All log_closed calls |
| 4 | SAVE exit classified as LOSS: peak $2+→drop to $0.50 is a PROFITABLE exit (+$0.50) but logged as outcome='LOSS' | `position_manager.py` | Line 185-188 |
| 5 | RSI criterion backwards for SELL: checks `rsi > 40` but bearish setups need RSI NOT oversold — should check `< 60` (or just accept any RSI that's not oversold, i.e. > 30) | `auto_scalper.py` score_setup() | Line 149 |
| 6 | Peak tracking starts from current profit: `peak = trade.get("peak_profit") or profit` — if peak_profit is 0 (null), uses current profit as initial peak, losing the first evaluation's true peak | `position_manager.py` | Line 114 |
| 7 | Profit factor denominator inverted: gross_wins / max(gross_losses, 0.01) — should be abs(gross_losses) | `trade_db.py` get_stats() | ~line 164 |

## Strategy Performance (Dry Test, 4 Completed Trades)

| Metric | Value |
|---|---|
| Win Rate | 50.0% (2W/2L) |
| Net P&L | +$3.84 |
| Avg Win | +$5.22 |
| Avg Loss | -$3.30 |
| Best Trade | +$5.30 (CLOSE_TARGET) |
| Worst Trade | -$3.44 (SL_HIT) |
| Avg Score | 6.0/7 |
| Max DD | $0.88 (2.8%) |

**NOTE:** All wins were CLOSE_TARGET ($4.50 auto-close), NOT TP_HIT ($6.00). TP is never reached. Consider either moving TP closer or removing the $4.50 auto-close and letting trades run to full TP.

## Top 20 Improvements (from the audit)

1. Fix calculation bugs (profit factor, bars_held, balance_after, SAVE classification)
2. Implement real market structure (BOS/CHoCH/FVG/OB)
3. Add economic calendar filter (NFP, FOMC, CPI)
4. Add ATR-based dynamic SL/TP
5. Enforce max daily drawdown (3%)
6. Wire up consecutive loss cooldown
7. Re-weight scoring criteria by actual predictive value
8. Implement position sizing (Kelly or fixed-fraction)
9. Prevent duplicate signals within N minutes
10. Add partial profit taking at 1:1 R:R
11. Fix SAVE classification to WIN (it's a profitable exit)
12. Add watchdog alerting (Telegram/email on bridge failure)
13. Add spread monitoring (skip trade if spread > 5× normal)
14. Add execution latency tracking
15. Add weekend/holiday check
16. Implement proper AMD with FVGs and Order Blocks
17. Track equity curve (Sharpe, Sortino, drawdown)
18. Add OBV divergence detection
19. Create human-readable trade journal in Obsidian
20. Containerize the RPyC bridge with auto-restart

## Data Sources

| Source | Symbol | Status |
|---|---|---|
| MT5 (ICMarkets Demo) | XAUUSD | Primary — live |
| yfinance | GC=F | Fallback — delayed |

## Database

- Path: `~/trading/data/trades.db`
- Tables: trades, rejected_signals, account_snapshots
- State files: scalper_state.json, position_state.json
- Trade log (legacy): trade_log.jsonl

## ESJ
