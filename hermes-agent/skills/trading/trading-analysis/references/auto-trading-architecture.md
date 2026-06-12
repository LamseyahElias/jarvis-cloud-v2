# Auto-Trading Architecture

## Components

### auto_scalper.py (every 3min, no_agent cron)
Opens new trades when conditions are met:
1. Check cooldown (15min after any loss)
2. Connect to MT5 via TradeExecutor
3. Skip if positions already open (max 1 at a time)
4. Skip if daily loss ≥ 3%
5. Run `xauusd_analyzer.run_analysis()` for market data
6. Determine direction from confluence bias (BEARISH → SELL, BULLISH → BUY)
7. Score setup 0-7 with `score_setup(results, direction)`
8. Only trade if score ≥ 4
9. Open with conservative parameters:
   - Small account: 0.01 lot, $7 SL, $10 TP
   - Standard account: 0.02 lot, $15 SL, $20 TP

### position_manager.py (every 2min, no_agent cron)
Manages open positions — THE CRITICAL COMPONENT:
1. Connect to MT5 via MT5Bridge directly (NOT TradeExecutor — see pitfall #16)
2. Call `mt5.initialize()` explicitly
3. Check daily loss limit → force close all if ≥ 3%
4. For each position:
   - Track peak profit in state file
   - Auto-close at +$8 (small account) or +$20 pips (standard)
   - Trail SL based on account-size-appropriate stages
   - Peak drawdown protection: close if profit drops to 30% of peak
   - Danger alerts at -$5 and -$8
5. Detect externally closed positions (SL/TP hit on MT5 side)

### xauusd_monitor.py (every 30min)
Market condition alerts — not trade execution.

### xauusd_analyzer.py (daily report + library)
Analysis engine used by auto_scalper. Provides `run_analysis()` function.

## Score Criteria (7 points)

1. **AMD Phase** — Manipulation or Distribution aligned with direction (+1)
2. **Confluence Bias** — Overall bias matches direction (+1)
3. **15m EMAs** — EMA9 vs EMA21 alignment (+1)
4. **1H Timeframe** — Higher TF bias alignment (+1)
5. **RSI** — Not overbought/oversold (RSI 30-70) (+1)
6. **MACD** — MACD line vs signal alignment (+1)
7. **Session** — London or NY active (+1)

## Bugs Found & Fixed (2026-05-22)

### Bug 1: get_tick() returns None after get_open_positions()
**Symptom:** Auto scalper scored 7/7 but produced no output. `get_tick('XAUUSD')` returned None.
**Root cause:** `TradeExecutor.get_open_positions()` calls `conn.root.exposed_get_positions()` which sometimes corrupts RPyC connection state. Subsequent `symbol_info_tick()` returns None.
**Fix:** Position manager v2 uses `MT5Bridge` directly instead of `TradeExecutor`. For auto_scalper, the issue is intermittent — adding retry or re-init after `get_open_positions` helps.

### Bug 2: SL/TP distances wrong for account size
**Symptom:** $15 SL on 0.02 lot = $30 risk on $55 account (55% risk!)
**Fix:** Small accounts use 0.01 lot, $7 SL, $10 TP.

### Bug 3: Position manager too slow
**Symptom:** Trade hit +$11, PM checked every 5min, profit dropped to $3 before next check.
**Fix:** Reduced to 2min interval + auto-close at +$8.

## State Files
- `~/trading/data/scalper_state.json` — cooldown, daily trade count
- `~/trading/data/position_state.json` — peak profits, open tickets
- `~/trading/data/trade_log.jsonl` — append-only trade log

## File Locations
- Scripts: `~/trading/scripts/`
- Hermes cron copies: `~/.hermes/scripts/` (must be synced after edits)
- Always `cp ~/trading/scripts/*.py ~/.hermes/scripts/` after changes
