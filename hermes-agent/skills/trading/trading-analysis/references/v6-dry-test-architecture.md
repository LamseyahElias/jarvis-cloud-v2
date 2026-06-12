# JARVIS Trading Engine v6 — Dry Test Architecture

> Part of the `trading/trading-analysis` umbrella. Detailed reference for the v6 system built June 2026.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         WSL (Linux)                               │
│                                                                   │
│  ┌──────────────────┐     ┌──────────────────┐                   │
│  │ auto_scalper.py   │     │ position_mgr.py  │                   │
│  │ (every 2m via     │     │ (every 1m via    │                   │
│  │  cron)            │     │  cron)            │                   │
│  └──────┬───────────┘     └──────┬───────────┘                   │
│         │                        │                              │
│  ┌──────▼────────────────────────▼──────────┐                   │
│  │           risk_manager.py                 │                   │
│  │  approve_trade(): 9 rules, stateful lock  │                   │
│  └────────────────────┬──────────────────────┘                   │
│                       │                                         │
│  ┌────────────────────▼──────────────────────┐                   │
│  │        market_protection.py                │                   │
│  │  news_filter → spread_filter → session    │                   │
│  │  → volatility_regime (advisory)           │                   │
│  └────────────────────┬──────────────────────┘                   │
│                       │                                         │
│  ┌────────────────────▼──────────────────────┐                   │
│  │       xauusd_analyzer.py + market_structure.py               │
│  │  EMAs/RSI/MACD/ATR/AMD + BOS/CHoCH/FVG/OB │                   │
│  └────────────────────┬──────────────────────┘                   │
│                       │                                         │
│  ┌────────────────────▼──────────────────────┐                   │
│  │              trade_db.py (SQLite)          │                   │
│  │  7 tables, 43+ columns, full audit trail  │                   │
│  └────────────────────┬──────────────────────┘                   │
│                       │                                         │
│  ┌────────────────────▼──────────────────────┐                   │
│  │           watchdog.py (every 5m)           │                   │
│  │  6 checks: bridge/cron/DB/risk/lag/system │                   │
│  └───────────────────────────────────────────┘                   │
│                                                                   │
│  ┌───────────────────────────────────────────┐                   │
│  │        dry_test_reporter.py               │                   │
│  │  11-section report on demand              │                   │
│  └───────────────────────────────────────────┘                   │
│                                                                   │
│         RPyC v6 ─── 172.26.128.1:18812                           │
│              Windows MT5 Terminal                                 │
└──────────────────────────────────────────────────────────────────┘
```

## Module Reference

### mt5_bridge.py v6 — RPyC Client
- Auto-retry on all critical methods (3 attempts, reconnect + re-init)
- `account_info()` → `exposed_get_account_info()` (dict: balance, equity, profit, margin, margin_free, leverage, name, server, currency)
- `positions_get()` → `exposed_get_positions()` (list of dicts)
- `modify_position(ticket, sl, tp)` → `exposed_modify_position()` (server helper, not raw order_send)
- `order_send(request)` → `exposed_send_order()` (keyword args, returns dict)
- Visible error logging to stderr for cron visibility
- **Double init:** `mt5.initialize(); mt5.initialize()` — fixes stale IPC

### auto_scalper.py v6 — Signal Generator (dry mode)
**Runs:** Every 2m via cron (no_agent: true, deliver: local)

**Flow:** Connect → account info → risk check → market protection check (news/spread/session) → tick → analysis + structure → direction → weighted scoring → ATR-based SL/TP → duplicate check → log PENDING to DB.

**Key settings:** DRY_MODE=True (hardcoded), MIN_SCORE=5 (was 4), MAX_TRADES_PER_DAY=50.

### position_manager.py v6 — Signal Evaluator
**Runs:** Every 1m via cron (no_agent: true, deliver: local)

**Flow:** Connect → tick → snapshot → get PENDING signals → check expiration (120min) → for each: compute virtual profit, track peak/MFE/MAE, log PARTIAL_1R event if at 1R, check SL→LOSS, TP→WIN, $4.50→WIN, peak$2.00→$0.50→SAVE.

### risk_manager.py — 9 Protection Rules
1. Daily drawdown ≥3% → lock
2. Weekly drawdown ≥6% → lock
3. 3 consecutive losses → 1h cooldown
4. 5 consecutive losses → day stop
5. 3 bridge failures → lock
6. Spread > $0.50 → reject
7. Weekend/market close → lock
8. SQLite health fail → lock
9. approve_trade() gate

State: `~/trading/data/risk_state.json`

### market_protection.py — Filter Coordinator
- NewsFilter: 132 hardcoded USD events, blocks 2h before/1h after
- SpreadFilter: 50-spread rolling window, >3σ or >$0.50=BLOCK
- SessionFilter: Asian (0-8)=BLOCK, Weekend=BLOCK, London/NY=5
- VolRegime: LOW/NORMAL/HIGH (advisory only)

### market_structure.py — 8 Analysis Functions
Swing points, BOS, CHoCH, FVG, Order Blocks, Liquidity Sweep, MTF Confluence, Full Analysis.

### trade_db.py v2 — SQLite Database
**Path:** ~/trading/data/trades.db | 7 tables, 43+ columns
Tables: trades, rejected_signals, account_snapshots, market_scans, bridge_health, partial_profits, _risk_health_check_v1.

### watchdog.py — 6 Health Checks
Bridge, cron, DB, risk, signal lag, system. Returns structured dict with alerts.

### dry_test_reporter.py — 11-Section Report
Run: `python3 ~/trading/scripts/dry_test_reporter.py` or `--verbose`.

## Strategy: ATR-Based 2:1 R:R

### SL/TP (v6)
```python
# Regime-adjusted:
# LOW: SL = max(2.0, ATR × 0.7)  — wider relative
# NORMAL: SL = max(3.0, ATR × 0.5)  — standard
# HIGH: SL = max(5.0, ATR × 0.3)  — tighter relative
TP = SL × 2  # maintain 2:1 R:R
```

### Weighted Scoring (max 11, min 5 to trade)

| Criterion | Points |
|---|---|
| AMD phase matching direction | 2 |
| Overall bias matching direction | 2 |
| 15m EMA alignment | 1 |
| 1H bias alignment | 1.5 |
| RSI in favorable zone (SELL:30-60, BUY:40-70) | 1 |
| MACD histogram alignment | 1 |
| Session (London/NY) | 0.5 |
| Market structure MTF confluence | 2 |
| **Penalty: conflicting 15m/1H** | -1 |
| **Penalty: no clear AMD phase** | -1 |
| **Penalty: RSI extreme (>70 or <30)** | -1 |

### Profit Management
- $0 → $2.00: HANDS OFF
- $2.00 → $4.50: Lock $1 (SL to entry ± $1.00)
- $4.50+: CLOSE
- Peak $2.00+ drops to $0.50: CLOSE (save)
- Signal expires after 120 min → EXPIRED (profit=0)

## State Files
- `~/trading/data/scalper_state.json` — trade counter, last signal
- `~/trading/data/position_state.json` — ticket tracker, open list
- `~/trading/data/risk_state.json` — risk manager state
- `~/trading/data/spread_history.json` — SpreadFilter rolling 50-window
- `~/trading/data/trades.db` — SQLite, 7 tables

## All 10 Original Bugs Fixed (v5→v6)
1. Profit factor: `max(abs(gross_losses), 0.01)` — uses absolute value
2. bars_held: computed from timestamp
3. balance_after: passed from actual MT5 balance
4. Daily P&L: preserved from DB stats
5. peak_profit: uses `is not None` check
6. SAVE: now WIN (captures profit)
7. RSI SELL: changed to `< 60`
8. Duplicate signals: prevents within $1 of last
9. State files: PM updates scalper state from DB
10. Trade counts: DB is single source of truth

## Commands
```bash
# Generate/evaluate signals, report, health check
python3 ~/trading/scripts/auto_scalper.py
python3 ~/trading/scripts/position_manager.py
python3 ~/trading/scripts/dry_test_reporter.py
python3 ~/trading/scripts/watchdog.py
```

## Pitfalls (v6 additions)
1. **Risk initial balance can be wrong.** If test signal uses fake balance ($10,000), drawdown % is absurd (99%+). Verify after init: `cat risk_state.json | grep start_balance`.
2. **Weekend check blocks Fri 21:00+ UTC.** Gold sometimes opens Sunday 22:00 UTC but session_filter doesn't catch it — only risk_manager does.
3. **News filter dates are hardcoded.** 132-event table has specific dates. Generic fallback: Wed/Thu/Fri 12:00-14:00 UTC.
4. **Spread history persists.** If market regime changes permanently, old data dilutes the rolling window.
5. **Dynamic WSL IP.** Bridge uses 172.26.128.1:18812. Can change on WSL restart. Verify: `ip route show default`.
6. **SQLite WAL mode.** Safe for single-writer, but kill during write can corrupt DB.
7. **Cron output dir may not exist.** Watchdog reports CRITICAL for cron on fresh install — expected.
