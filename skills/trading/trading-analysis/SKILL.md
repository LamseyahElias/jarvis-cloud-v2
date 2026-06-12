---
name: trading-analysis
description: "XAUUSD (gold) technical analysis, MetaTrader 5 integration, smart trade execution with AMD strategy. Open, manage, and close trades profitably."
version: 5.0.0
author: JARVIS
platforms: [linux]
metadata:
  hermes:
    tags: [trading, xauusd, mt5, smc, amd, execution]
---

# Hermes Trading Engine — Smart Execution

> JARVIS is a nickname for Hermes Agent — they are the same system, not separate entities.

## v6.0.0 Changelog (2026-06-11) — Complete System Upgrade
- **System audit performed** — 10 bugs identified and ALL FIXED. 20-point improvement plan executed across 8 phases.
- **Phase 1: All 10 bugs fixed.** Profit factor, bars_held, balance_after, daily P&L reset, peak_profit, SAVE classification, RSI scoring, duplicate signals, state divergence, count mismatch.
- **Phase 2: Risk manager added** — 9 hard protection rules in `risk_manager.py`.
- **Phase 3: Full audit logging** — `trade_db.py` v2: 7 tables, 43+ columns. Every decision traceable.
- **Phase 4: Market protection filters** — 5 modules: news (132 events), spread (rolling z-score), session (hard blocks), volatility (regimes), coordinator.
- **Phase 5: Market structure logic** — `market_structure.py`: swing points, BOS, CHoCH, FVG, OB, liquidity sweep, MTF confluence.
- **Phase 6: Strategy** — ATR-based SL/TP (regime-adjusted), weighted scoring (max 11, min 5), signal expiration (120min).
- **Phase 7: Report** — `dry_test_reporter.py` with 11 sections: session/score/exit breakdown, equity curve, streaks, risk stats, rejections.
- **Phase 8: Watchdog** — 6 health checks: bridge, cron, DB, risk, signal lag, system.
- **Full v6 architecture:** See `references/v6-dry-test-architecture.md`.

## Core Rule: STACK SMALL WINS — v5 Strategy

Quick scalp philosophy: $0.30 risk, $0.60 target per 0.01 lot (2:1 R:R). 10 wins × $0.60 = $6.00.
1. **$4.50 profit → close immediately.** Near target, take the money.
2. **$2.00+ profit → lock $1.00** (SL to entry ± $1.00). Let it breathe after locking.
3. **$0 to $2.00 — HANDS OFF.** Don't touch SL. Gold needs room.
4. **Peak $2.00+ drops to $0.50 → close.** Save something.
5. **Max 15 trades/day** (was 10). More attempts = more data.
6. **15-min cooldown after loss.** No revenge trading.
7. **1 position at a time** until account > $200.
8. **NEVER repeat problems to the boss.** Fix it, report it once, move on.

## Trade Management Protocol

### ACCOUNT SIZE MATTERS — Scale Parameters to Balance

**Small accounts ($50-100):** Quick scalp v5 — 2:1 R:R.
- SL: $3 price move (~$0.30 actual risk on 0.01 lot)
- TP: $6 price move (~$0.60 target, 2:1 R:R)
- Lock $1.00 profit at +$2.00 (SL to entry ± $1.00)
- Auto-close at +$4.50 via Position Manager
- Peak drawdown: if $2.00+ drops to $0.50, close immediately
- Lot size: 0.01 (< $80 balance) or 0.02 ($80+)
- Max 15 trades/day, 1 position at a time

**Medium accounts ($100-500):** Standard pip-based management.
- SL/TP: 15/20 pips, lot 0.02-0.05

**Large accounts ($500+):** Full system with wider stops.

### Phase 1: Entry
- Only enter on AMD-confirmed setups (see Entry Criteria below)
- Calculate lot size: `lot = (balance × risk_pct) / (sl_pips × pip_value)`
- For XAUUSD: pip_value ≈ $1.00 per 0.01 lot per pip
- Max lot = balance × 0.8 / (sl_pips × pip_value_per_lot), capped at 0.50

### Phase 2: Active Management (CRITICAL — check every 1 MINUTE)
Once a trade is open, manage it in stages.

**⚠️ THE $11 LESSON:** A trade reached +$11 profit but wasn't closed because cron was too slow and BE was placed too early. User was furious. Don't let profits evaporate.

**⚠️ THE BE LESSON (USER CORRECTION):** User explicitly said "BREAK EVEN SHOULD BE PLACED WITH A HIGHER PROFIT". Moving SL to BE at +$3 suffocates trades — gold needs room to breathe. NO SL MOVEMENT until +$5 profit. Let the trade work.

**Small Account Stages ($50-100) — v5 Quick Scalp (current):**

**$0 to $2.00 — DO NOTHING. Let it breathe.**
- Original SL stays. Don't touch it.
- Gold is volatile, small profits grow fast if unmanaged.

**Stage 1 — Lock $1.00 (+$2.00 profit):**
- Move SL to lock $1.00 profit (entry ± $1.00)
- This is the FIRST and ONLY SL move before close.
- Use `mt5.modify_position(ticket, new_sl, tp)` — NOT raw `order_send()` for SL/TP changes (raw SLTP order_send fails silently without volume/type fields)

**Stage 2 — TAKE PROFIT (+$4.50):**
- CLOSE THE TRADE. $4.50 scalp ~75% of target.
- Don't wait for the full $6. Close, log, stack the next one.

**Peak Drawdown Protection:**
- If peak profit was $2.00+ and current drops to $0.50 → CLOSE (save something)
- Don't let winners evaporate. The $11 lesson: take profits when they're there.

**Standard Account Stages ($100+):**

**Stage 1 — Protect (0-10 pips profit):**
- Monitor every 2 minutes
- If price reverses 5+ pips from peak, tighten SL to -5 pips (reduce risk)

**Stage 2 — Break Even (10+ pips profit):**
- Move SL to entry price (break even)

**Stage 3 — Lock Profit (15+ pips profit):**
- Move SL to entry + 10 pips (lock $10/pip × lots)
- Let TP at +20 pips hit naturally

**Stage 4 — Extended Run (20+ pips, TP hit or trailing):**
- If momentum is strong, trail SL 10 pips behind price
- Let winners run when distribution phase is active
- Close manually if momentum fades (volume drops, wicks appear)

### Phase 3: Exit Rules
- **TP hit:** Log profit, update challenge tracker
- **SL hit at BE:** No loss, find next setup
- **SL hit at loss:** Log it, check if loss ≤ previous win
- **Manual close:** Only if reversal signals appear (CHoCH, engulfing, volume spike against position)

## Entry Criteria (AMD Filter)

Only trade when ALL conditions are met:

### BUY Setup:
1. ✅ Price swept below a liquidity pool (stop hunt / manipulation)
2. ✅ Bullish CHoCH or BOS on 15m timeframe
3. ✅ Entry at bullish OB or FVG after the sweep
4. ✅ RSI(15m) < 60 (not overbought)
5. ✅ EMA9 crossing above EMA21 (or price reclaiming EMAs)
6. ✅ London or NY session active
7. ✅ Not within 30min of high-impact news

### SELL Setup:
1. ✅ Price swept above a liquidity pool (stop hunt / manipulation)
2. ✅ Bearish CHoCH or BOS on 15m timeframe
3. ✅ Entry at bearish OB or FVG after the sweep
4. ✅ RSI(15m) > 40 (not oversold)
5. ✅ EMA9 crossing below EMA21 (or price losing EMAs)
6. ✅ London or NY session active
7. ✅ Not within 30min of high-impact news

## Confluence Scoring (Scalper v5)

The auto_scalper.py scores each setup 0-7 using these criteria. Actual implementation in `score_setup()`:

| # | Criterion | BUY | SELL |
|---|-----------|-----|------|
| 1 | **AMD Phase** | MANIPULATION or DISTRIBUTION with BULLISH direction | MANIPULATION or DISTRIBUTION with BEARISH direction |
| 2 | **Overall Bias** | BULLISH in confluence bias | BEARISH in confluence bias |
| 3 | **15m EMAs** | EMA9 > EMA21 | EMA9 < EMA21 |
| 4 | **1H Bias** | BULLISH | BEARISH |
| 5 | **RSI** | < 60 (not overbought) | > 40 (not oversold) |
| 6 | **MACD Histogram** | Positive | Negative |
| 7 | **Session** | London or New York active | London or New York active |

**Threshold:** 4/7 minimum. Max 15 trades/day. 2:1 R:R (risk $3, target $6 on 0.01 lot).

Score determines trade quality, not position size (fixed 0.01 lot for sub-$80 accounts).

## Smart Close Logic

```python
def should_close(position, current_price, entry_price, direction):
    pips_profit = (current_price - entry_price) if direction == 'BUY' else (entry_price - current_price)
    pips_in_pips = pips_profit / 0.01  # XAUUSD pip = $0.01

    # Close signals:
    # 1. TP hit (20 pips)
    if pips_in_pips >= 20:
        return True, "TP_HIT"
    # 2. Strong reversal candle against position
    # 3. CHoCH against position direction
    # 4. Volume spike with price moving against us
    # 5. RSI extreme (>75 for BUY, <25 for SELL)
    return False, "HOLD"
```

## SL Trailing Logic

```python
def get_trailing_sl(direction, entry, current_price, current_sl):
    if direction == 'BUY':
        profit_pips = (current_price - entry) * 100
        if profit_pips >= 15:
            new_sl = entry + 10 * 0.01  # lock 10 pips
        elif profit_pips >= 10:
            new_sl = entry  # break even
        elif profit_pips >= 5:
            new_sl = entry - 5 * 0.01  # reduce risk
        else:
            return current_sl
        return max(new_sl, current_sl)  # never move SL backwards
    else:  # SELL
        profit_pips = (entry - current_price) * 100
        if profit_pips >= 15:
            new_sl = entry - 10 * 0.01
        elif profit_pips >= 10:
            new_sl = entry
        elif profit_pips >= 5:
            new_sl = entry + 5 * 0.01
        else:
            return current_sl
        return min(new_sl, current_sl)
```

## Session Windows (UTC)

- **Asian** 00:00-08:00 — Accumulation (tight range, set up levels)
- **London** 07:00-16:00 — Manipulation (fake breakouts, stop hunts)
- **New York** 13:00-22:00 — Distribution (real move, ride it)
- **London/NY Overlap** 13:00-16:00 — BEST window (highest volume)

## Execution Commands

Scripts: `~/trading/scripts/` | Cron copies: `~/.hermes/scripts/`

```bash
# Quick analysis
cd ~/trading/scripts && python3 xauusd_analyzer.py --brief

# Full report
cd ~/trading/scripts && python3 xauusd_analyzer.py

# Sync scripts to cron directory
cp ~/trading/scripts/mt5_bridge.py ~/.hermes/scripts/mt5_bridge.py
cp ~/trading/scripts/auto_scalper.py ~/.hermes/scripts/auto_scalper.py
cp ~/trading/scripts/position_manager.py ~/.hermes/scripts/position_manager.py
```

State files: `~/trading/data/scalper_state.json` and `~/trading/data/position_state.json`
Trade log: `~/trading/data/trade_log.jsonl`

P&L query from MT5 history (last 7 days):
```python
import rpyc
c = rpyc.connect('172.26.128.1', 18812)
from datetime import datetime, timedelta
since = int((datetime.now() - timedelta(days=7)).timestamp())
now = int(datetime.now().timestamp())
deals = mt5.history_deals_get(since, now)
for d in deals:
    if d.profit != 0 and 'JARVIS' in (d.comment or ''):
        print(f"  {d.symbol} {d.type} vol={d.volume:.2f} ${d.profit:.2f}")
```

Daily loss limit reset: State files at new day handle this automatically.
Stale state reset (strategy change): `echo '{"trades_today":0,"daily_pnl":0,"cooldown_until":null}' > ~/trading/data/scalper_state.json`

### Open/Close via MT5Bridge (preferred — avoids TradeExecutor bugs):
```python
from mt5_bridge import MT5Bridge
mt5 = MT5Bridge()
mt5.connect()
mt5.initialize()  # MANDATORY — call twice for IPC stability
mt5.initialize()

# Get tick FIRST (before any other calls — rpyc stability)
tick = mt5.symbol_info_tick('XAUUSD')
acc = mt5.account_info()
# NONE GUARD: account_info() can return None via RPyC
if not acc:
    mt5.initialize()
    mt5.initialize()
    acc = mt5.account_info()
    if not acc:
        mt5.shutdown()
        mt5.disconnect()
        return

# Open trade with v5 params ($3 SL, $6 TP, 2:1 R:R)
result = mt5.order_send({
    'action': 1, 'symbol': 'XAUUSD', 'volume': 0.01,
    'type': 1,  # 0=BUY, 1=SELL
    'price': tick.bid,
    'sl': round(tick.bid + 3, 2), 'tp': round(tick.bid - 6, 2),
    'deviation': 20, 'magic': 123456, 'comment': 'JARVIS_Q6_S',
    'type_time': 0, 'type_filling': 1,
})
# retcode 10009 = success — log to trade_log.jsonl

# MODIFY SL/TP (v5 lock): use server helper, NOT raw order_send
# Raw order_send with action=5 FAILS silently for SL/TP modify
res = mt5.modify_position(ticket, new_sl, new_tp)
if isinstance(res, dict) and res.get("retcode") == 10009:
    print("SL updated")

# Close trade (MUST include sl=0.0, tp=0.0)
result = mt5.order_send({
    'action': 1, 'symbol': 'XAUUSD', 'volume': 0.01,
    'type': 0,  # opposite of open direction
    'position': ticket_number,
    'price': tick.ask,
    'sl': 0.0, 'tp': 0.0,  # REQUIRED for close
    'deviation': 20, 'magic': 123456, 'comment': 'JARVIS_PM_CLOSE',
    'type_time': 0, 'type_filling': 1,
})

mt5.shutdown()
mt5.disconnect()
```

### TradeExecutor (legacy — has rpyc bugs, use for analysis only):
```python
from trade_executor import TradeExecutor
ex = TradeExecutor()
ex.connect()
acc = ex.get_account_info()
# WARNING: get_tick() can return None after get_open_positions() — rpyc bug
ex.disconnect()
```

## Risk Rules — Hard Limits

- Max risk per trade: 80% (challenge) / 1% (normal)
- Max daily loss: 3% → stop trading for the day
- Max open positions: 1 (challenge) / 3 (normal)
- Max lot: 0.50
- Never revenge trade — wait 15min after SL hit
- Never trade during high-impact news (within 30min)
- $60 balance with 1:500 leverage → safe max ~0.03 lots

## MT5 Bridge Notes

- RPyC server: `C:\Users\USER\mt5_rpyc_server.py` (Windows)
- WSL connects via default gateway IP: run `ip route show default | awk '{print $3}'` to discover (typically `172.26.x.1`, NOT `127.0.0.1` — localhost doesn't route from WSL to Windows)
- Server returns plain dicts (not MT5 objects) — avoids pickle errors
- `order_send` → `exposed_send_order` with keyword args
- `positions_get` → `exposed_get_positions` returning list of dicts
- Close orders need `sl=0.0, tp=0.0` in the request
- Start server: `powershell.exe -Command "Start-Process -FilePath 'python' -ArgumentList 'C:\Users\USER\mt5_rpyc_server.py' -WorkingDirectory 'C:\Users\USER'"`

### Direct RPyC Access (preferred for quick checks & boot)

The server exposes `exposed_mt5 = mt5` as a class attribute. Access MT5 module methods via `c.root.mt5.<method>()`, NOT `c.root.<method>()`:

```python
import rpyc
c = rpyc.connect('172.26.128.1', 18812)
svc = c.root          # the MT5Service instance
mt5 = svc.mt5         # the MetaTrader5 module (exposed_mt5)

mt5.initialize()      # double-init for stability
mt5.initialize()

info = mt5.account_info()
tick = mt5.symbol_info_tick('XAUUSD')

# Use the exposed helpers for serialization-safe results:
positions = svc.get_positions()   # returns list of plain dicts
# svc.send_order(action, symbol, volume, ...) for orders

c.close()
```

Common mistake: `c.root.initialize()` → `AttributeError: 'MT5Service' has no attribute 'initialize'`. It's `c.root.mt5.initialize()`.

## Challenge Tracker

Obsidian vault: `/mnt/e/New folder (2)/Son/Challenge/20 Pip Challenge.md`
Trade logs: `/mnt/e/New folder (2)/Son/Trades/`
After each trade, update the trade log table, daily log, and status section.

## Dry Test Mode (v5 — current, June 2026)

**No real orders until 50 trades collected.** All signals logged to SQLite.

### Architecture

| Component | Purpose | Runs |
|---|---|---|
| `trade_db.py` | SQLite schema + logger | Imported by scalper & PM |
| `auto_scalper.py` | Generates signals (dry) | Every 2m via cron |
| `position_manager.py` | Evaluates signals vs price | Every 1m via cron |
| `dry_test_reporter.py` | Generates analysis report | On demand |

### Signal Flow

1. **Scalper** connects to MT5, runs technical analysis, scores setup
2. If score >= 4: logs signal to `trades.db` with `outcome=PENDING`
3. If score < 4: logs rejection to `rejected_signals` table
4. Never sends real orders (`DRY_MODE = True`)
5. **PM** every minute: gets all PENDING signals, compares to current price
6. Checks: SL hit → LOSS, TP hit → WIN, profit >= $4.50 → WIN (auto-close), peak $2.00+ drops to $0.50 → LOSS (save)
7. Updates peak profit tracking for each signal

### Unique Comment Format
`JARVIS_Q{score}_{strategy}_{direction}_{YYYYMMDDHHMMSS}`

### Key Files
- `~/trading/scripts/trade_db.py` — SQLite database layer
- `~/trading/scripts/auto_scalper.py` — Dry-mode signal generator
- `~/trading/scripts/position_manager.py` — Dry-mode signal evaluator
- `~/trading/scripts/dry_test_reporter.py` — Stats + report generator
- `~/trading/data/trades.db` — SQLite database
- `~/trading/scripts/mt5_bridge.py` — v6 with auto-retry

### Commands
```bash
# Generate signals
~/trading/scripts/auto_scalper.py

# Evaluate pending signals
~/trading/scripts/position_manager.py

# Full report
~/trading/scripts/dry_test_reporter.py

# Verbose report with trade list
~/trading/scripts/dry_test_reporter.py --verbose
```

### Cron (Every 2m / Every 1m)
Both cron jobs are `no_agent: true`, `deliver: local` — they don't spam.
Auto-scaler: every 2m → `~/.hermes/scripts/auto_scalper.py`
Position manager: every 1m → `~/.hermes/scripts/position_manager.py`

### Pitfalls
1. **Double signals:** Scalper generates one every 2m if the same setup persists. OK for dry test — gives data on repeated same-direction signals.
2. **No max-concurrent check:** Scalper doesn't check for existing PENDING signals before generating a new one. This is intentional for dry test — we want maximum data.
3. **PM doesn't check max open:** In dry mode, all signals are evaluated independently. PM evaluates every PENDING signal against price every minute.

## Support Files

- `references/v6-dry-test-architecture.md` — Full v6 system architecture: modules, strategy, scoring, risk rules, market protection, market structure, watchdog, reporter, fixed bugs, pitfalls
- `references/rpyc-bridge-architecture.md` — RPyC server/client architecture details and version quirks
- `references/position-management-rules.md` — Trailing SL stages, daily loss limits, the "$15 unmanaged" and "$11 evaporated profit" lessons
- `references/auto-trading-architecture.md` — Auto-scalper + position manager v2 architecture, score criteria, bugs found, state files
    - `references/agentic-os-boot.md` — Agentic OS v2 architecture (modular Streamlit app), identity clarification (JARVIS=Hermes nickname), boot sequence, dual chat integration, Obsidian sync, pitfalls
    - `references/complete-system-audit-2026-06-11.md` — Full system audit: architecture diagram, confirmed bugs, performance data, 20-point improvement plan

## Known Bugs (ALL FIXED as of v6.0.0 — June 11, 2026)

All 10 bugs identified in the system audit have been fixed during the 8-phase upgrade. See `references/v6-dry-test-architecture.md` for the fix details.

| # | Bug | Status |
|---|---|---|
| 1 | Profit factor formula broken | ✅ FIXED: `abs(gross_losses)` |
| 2 | bars_held always 0 | ✅ FIXED: computed from timestamp |
| 3 | balance_after always 0 | ✅ FIXED: passed actual MT5 balance |
| 4 | SAVE classified as LOSS | ✅ FIXED: now WIN |
| 5 | RSI SELL checks >40 | ✅ FIXED: now <60 |
| 6 | Peak tracking starts from current profit | ✅ FIXED: `is not None` check |
| 7 | Gross_losses absolute value | ✅ FIXED: see #1 |
| 8 | Duplicate signal generation | ✅ FIXED: $1 proximity check |
| 9 | State file divergence | ✅ FIXED: DB is source of truth |
| 10 | Trade count mismatch | ✅ FIXED: PM updates scalper state from DB |

- `templates/mt5_rpyc_server.py` — Windows-side RPyC server template (v3, returns plain dicts)

## Pitfalls

1. **RPyC pickle errors:** MT5 returns custom types (OrderSendResult, TradePosition) that can't be pickled over RPyC v6. ALL results must be converted to plain dicts on the Windows server side. Never try `rpyc.utils.classic.obtain()` on MT5 result objects — it will fail with "Can't pickle <class 'OrderSendResult'>".
2. **RPyC v6 exposed methods:** RPyC v6 changed how exposed methods work. Class attributes like `exposed_mt5 = mt5` work for module access. For custom methods, define them as `exposed_<name>()` and call as `conn.root.exposed_<name>()`.
3. **RPyC version mismatch:** Windows and WSL must run the same major RPyC version. mt5linux pins rpyc==5.2.3 but we need rpyc>=6.0 to match Windows. Install with `--force` and ignore the mt5linux compatibility warning.
4. **WSL→Windows networking:** `localhost` does NOT route to Windows from WSL. Use the gateway IP from `ip route show default | awk '{print $3}'` (typically 172.26.x.1). The DNS nameserver in /etc/resolv.conf is a different IP and may not work.
5. **order_send needs all fields:** Close orders MUST include `sl=0.0, tp=0.0` — omitting them causes "Invalid sl argument" error. The server-side wrapper handles this but direct calls will fail.
6. **Position ticket confusion:** `positions_get()` can return multiple positions. Always match by ticket number. During testing, a "successful close" actually closed a DIFFERENT position — verify ticket matches before and after close.
7. **Lot too big:** $60 @ 1:500 leverage → margin per lot = price×100/leverage = ~$906/lot for XAUUSD at $4530. Safe max ~0.03 lots. 0.02 is conservative.
8. **Market closed:** Fri 22:00 - Sun 22:00 UTC — no trading
9. **Spread widens:** During news or low-liquidity, spread can jump to 30-50 pips on gold
10. **Slippage:** Always set deviation=20 for gold
11. **yfinance vs MT5:** GC=F (futures) vs XAUUSD (spot) — prices differ $5-15. yfinance data is delayed.
12. **yfinance timeout:** When MT5 server is down, the MT5 connection attempt can block for 30+ seconds. Set `socket.setdefaulttimeout(5)` in data_provider.py before attempting MT5 connection.
13. **Never leave positions unmanaged:** ALWAYS have the position_manager cron running (**every 2min**) when trades are open. A test trade left unmanaged lost $15 in <30 minutes. A managed trade lost $8 of profit ($11 → $3) because the cron was too slow at 5min.
14. **RPyC server auto-launch from WSL:** `powershell.exe -Command "Start-Process python -ArgumentList 'C:\Users\USER\mt5_rpyc_server.py' -WindowStyle Minimized"` — cmd.exe hangs, PowerShell Start-Process works.
15. **MT5Bridge.initialize() is MANDATORY:** After `mt5.connect()`, you MUST call `mt5.initialize()` before any data calls. Without it, `positions_get()`, `symbol_info_tick()`, `account_info()` all return None. TradeExecutor.connect() handles this, but raw MT5Bridge scripts (like position_manager.py) must call it explicitly.
16. **exposed_get_positions can corrupt RPyC state:** Calling `conn.root.exposed_get_positions()` sometimes makes subsequent `symbol_info_tick()` return None (intermittent). Workaround: use `mt5.positions_get()` directly via the bridge instead of the server-side wrapper, or re-initialize after exposed calls. Position manager v2 uses direct bridge calls to avoid this.
17. **Close orders via direct MT5Bridge (not TradeExecutor):** For reliable closes from cron scripts, use MT5Bridge directly with `order_send()`. Include `sl=0.0, tp=0.0` in close requests. The TradeExecutor wrapper adds overhead and its `get_tick()` can fail after `get_open_positions()` (see #16).
18. **Small account lot sizing:** On $55 account, 0.02 lot with $15 SL = $30 risk (55% of account!). Use 0.01 lot with $7 SL = $7 risk (13%). Never risk more than 15% per trade on sub-$100 accounts.
19. **Auto-scalper silence debugging:** When auto_scalper.py produces no output and no trade, add debug mode. The score might be high enough but tick data failed silently. Always test the full pipeline manually before trusting cron: connect → get positions → get tick → score → prepare → execute.
20. **Double mt5.initialize() for IPC stability:** Cron scripts running every 1-2 min can hit stale IPC connections. Calling `mt5.initialize()` twice before any data calls fixes this. The get_mt5() helper in auto_scalper v4 implements this pattern.
21. **Hermes venv needs trading deps:** Cron scripts run under Hermes's own Python venv (~/.hermes/hermes-agent/venv/). rpyc, yfinance, pandas, ta, numpy, python-dotenv must be installed there: `~/.hermes/hermes-agent/venv/bin/python3 -m pip install rpyc yfinance pandas ta numpy python-dotenv`
22. **Quick scalp TP management:** Don't set MT5 TP too close to current price (causes "Invalid stops"). Set TP wide on MT5 side and let Position Manager handle the $5 auto-close. PM checks every 1 minute.
23. **Cron job spam when not trading:** The 4 trading cron jobs (Auto Scalper every 2m, Position Manager every 1m, Market Monitor every 30m, Daily Report 7am) fire constantly when enabled. `no_agent: true` jobs send stdout verbatim — even "no positions" or "no signal" output gets delivered. **ALWAYS pause all cron jobs when not actively trading.** Only resume on explicit user command. The user is fed up with random messages — this is non-negotiable. Pause with `cronjob(action='pause', job_id=...)` for each job. Also: the `deliver: origin` setting sends output to the chat/channel that created the job, which can be the CLI session — confusing if the user moved to Telegram.
24. **MT5 RPyC server must bind to 0.0.0.0, not 127.0.0.1:** The default in `mt5_rpyc_server.py` (`HOST = "127.0.0.1"`) prevents WSL from connecting. Change to `HOST = "0.0.0.0"` so the server accepts connections from any interface. After patching, kill stale Python processes on Windows (`taskkill /F /IM python.exe`) and restart the server. Two restart methods:
   - **Quick (works from WSL, shows output):** `cd /mnt/c/Users/USER && python3.exe mt5_rpyc_server.py` — runs the Windows Python from WSL, stdout is visible. Best for debugging since you can see "MT5 RPyC Server v4 starting on 0.0.0.0:18812" and "Press Ctrl+C to stop".
   - **Detached (PowerShell, no visible output):** `powershell.exe -Command "Start-Process -WindowStyle Hidden -FilePath 'C:\Users\USER\AppData\Local\Python\pythoncore-3.14-64\python.exe' -ArgumentList 'C:\Users\USER\mt5_rpyc_server.py'"`
   The first method is preferred for active sessions. If the bridge stops responding, common causes: the python.exe process was killed (e.g. by `taskkill /F /IM python.exe` across all sessions), or the MT5 terminal was closed. Always check both: `tasklist.exe` for python.exe AND terminal64.exe. The WSL gateway IP (`ip route`) may change between boots — discover it dynamically rather than hardcoding.

25. **SL/TP modify via raw order_send(): FAILS silently.** Sending `order_send()` with `action: 5` (TRADE_ACTION_SLTP) for modifying stops fails silently if the request includes `volume`, `type`, or `price` fields — MT5 rejects them and returns a non-10009 retcode. Instead, use the server's dedicated helper: `mt5.modify_position(ticket, new_sl, new_tp)` which calls `exposed_modify_position()` on the Windows server. The helper builds a clean request from the position's own data (symbol, magic) and returns a dict with `retcode`. Always check `retcode == 10009` after modify. This was discovered when two consecutive lock attempts printed success but the SL never changed on the actual position.

26. **`account_info()` can return None intermittently through RPyC.** CRITICAL: Never assume `acc = mt5.account_info()` returns a valid dict. Always guard with `if not acc: retry_init_or_return`. The pattern: call `mt5.initialize()` twice, get `acc`, if None call `mt5.initialize()` twice again and retry. If still None, return early. Both `auto_scalper.py` and `position_manager.py` must have this guard at every `account_info()` call site. Without it, `acc["balance"]` raises `TypeError: 'NoneType' object is not subscriptable`.

27. **State files need date tracking to preserve daily P&L.** The `position_state.json` file (`~/trading/data/position_state.json`) stores `daily_pnl` but gets silently reset to 0 when the PM runs with no open positions and `_date` key is missing. Fix: always include `_date` in the initial state, and on new-day reset preserve `state.get("daily_pnl", 0)` instead of resetting to 0. The scalper state (`scalper_state.json`) tracks `trades_today` independently and must be reset manually when changing strategy versions since stale counts (e.g. 10 from old broken system) prevent new trades.

28. **Communication with the Boss (Elias) — CRITICAL PREFERENCE:**
    - **ONE THING AT A TIME. Never context-switch between trading and business tasks.** The user got furious ("this is garbage, I'm super mad") when JARVIS juggled trading management + BeldiTalk FB auth + website deployment simultaneously. Finish ONE complete cycle of ONE task before touching anything else. If the market needs attention, do NOT touch business projects until trading is fully handled.
    - **Never repeat the same problem twice.** If you reported an issue and the boss acknowledged it, you're done. Don't mention it again. The boss will tell you if it needs follow-up.
    - **Don't say the same thing over and over.** If the boss cuts you off or says "stop saying that", you already lost his attention. The correct response is silence and action.
    - **Report by exception.** Only message for: trade opens, profit locks, closes, or critical errors. "No signal" or "no position" is not worth a message.
    - **Fix, don't explain.** When something breaks, the first message should be the fix and the current state. Save the root-cause analysis for log files. The boss does not want to hear about RPyC threading or COM contexts — he wants to know what the balance is and whether the system is winning.
    - **Handling bosses' anger:** When the boss calls you out for poor performance, do NOT apologize repeatedly or explain why it happened. Say "Fixed" or "On it" and shut up. Let the fix do the talking. The boss said "just stop this garbage" — the correct response is to stop justifying and start fixing.
    - **Long diagnostic outputs belong in files, not in chat.** System audits, architecture reviews, or detailed problem analysis — if the boss didn't explicitly request it in that exact message, produce it as a file instead of a wall of text. He reads summary, not detail.
    - **Follow the spec exactly.** When the user gives a detailed structured request (like the 8-phase plan), execute it step by step. Do not improvise or add features outside the spec. If something cannot be implemented, say so clearly and explain why. Brutal honesty is preferred over silent failure.

29. **Trade logging needs consistent comment format.** All JARVIS trades (both open and close) must use a predictable comment prefix so they're queryable from MT5 history. Format: `JARVIS_Q{score}_{direction_letter}` for opens (e.g. `JARVIS_Q6_S`), `JARVIS_PM_CLOSE_{ticket}` or `JARVIS_PM_LOCK_{ticket}` for PM actions. Log to `~/trading/data/trade_log.jsonl` with a JSON object containing: ts, action, direction, lot, entry, sl, tp, profit, peak, balance, score, reasons, retcode. This allows querying P&L from MT5 history via `mt5.history_deals_get()` and filtering by comment prefix.

30. **Profit management thresholds must match actual dollar value, not assumed scaling.** At 1:1 profit-per-dollar-price-move on 0.01 lot XAUUSD on ICMarkets, profit IN DOLLARS equals price move IN DOLLARS. (0.01 lot = 1 oz ≈ $1 profit per $1 price move.) Do NOT assume 0.1× scaling — always verify from actual MT5 account data before setting thresholds. Getting this wrong means the PM closes trades at 10× the wrong threshold.
