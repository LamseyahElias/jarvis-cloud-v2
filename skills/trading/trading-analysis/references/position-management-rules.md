# Position Management Rules

## The Lesson That Cost $15 (Unmanaged Test Trade)

On 2026-05-22, a test trade (BUY 0.02 @ 4534.02) was left open while debugging the close function. The "close" actually closed a DIFFERENT position (different ticket). The original position drifted -$16 before being discovered 30+ minutes later.

**Root cause:** `positions_get()` returned multiple positions. The close logic didn't verify the ticket matched.

**Fix:** 
1. Built `position_manager.py` cron that monitors ALL open positions
2. Close function now matches by ticket explicitly
3. After every close, verify `get_open_positions()` returns 0 (or expected count)

## The $11 That Got Away (Profit Evaporated)

Same session: a SELL trade hit +$11 profit but position manager was running every 5min with thresholds calibrated for large accounts. By the time the user noticed, profit had dropped to $3.42. User was furious.

**Root causes:**
1. Position manager ran every 5min — too slow for volatile gold
2. Trailing SL thresholds were pip-based (10/15/20 pips) — meaningless on a $55 account
3. No auto take-profit. The system waited for TP at $20 distance instead of banking $11

**Fix (Position Manager v2):**
1. Cron interval: **every 2 minutes** (not 5)
2. Dollar-based thresholds for small accounts:
   - +$1.50 → reduce risk (SL to entry - $3)
   - +$3.00 → break even (SL to entry + $0.50)
   - +$5.00 → lock $3 profit (SL to entry + $1.50)
   - +$8.00 → **AUTO CLOSE** (take the money)
3. Peak drawdown protection: if profit drops to 30% of peak → close
4. Run as `no_agent=true` cron (direct stdout delivery, no LLM overhead)

## Trailing SL Stages — Small Account ($50-100, dollar-based)

| Profit ($) | Action | New SL | Effect |
|-----------|--------|--------|--------|
| 0-1.50 | Hold | Original SL | Full risk |
| 1.50-3.00 | Reduce risk | Entry - $3 | Risk cut in half |
| 3.00-5.00 | Break even | Entry + $0.50 | Risk-free + buffer |
| 5.00-8.00 | Lock profit | Entry + $1.50 | Guaranteed $3+ |
| 8.00+ | **CLOSE** | N/A | Take the money |

## Trailing SL Stages — Standard Account ($100+, pip-based)

| Profit (pips) | Action | New SL | Effect |
|--------------|--------|--------|--------|
| 0-5 | Hold | Original SL | Full risk |
| 5-10 | Reduce risk | Entry - 5 pips | Risk cut in half |
| 10-15 | Break even | Entry price | Risk-free trade |
| 15-20 | Lock profit | Entry + 10 pips | Guaranteed $10/pip×lots |
| 20+ (TP) | Close or trail | Entry + 15 pips | Let winners run |

## SL Modification via MT5

Use `TRADE_ACTION_SLTP` (action=6):
```python
mod_req = {
    "action": 6,  # TRADE_ACTION_SLTP
    "symbol": "XAUUSD",
    "volume": position_volume,
    "type": position_type,
    "position": ticket,
    "price": current_price,
    "sl": new_sl,
    "tp": existing_tp,
    "deviation": 20,
    "magic": 123456,
    "comment": "JARVIS_TRAIL",
    "type_time": 0,
    "type_filling": 1,
}
```

## Daily Loss Limit

- **Threshold:** 3% of balance
- **Check:** `abs(account.profit) / account.balance * 100 >= 3.0`
- **Action:** Force-close ALL open positions immediately
- **Cooldown:** No more trades until next trading day

## Cron Jobs (Current Setup)

- `position_manager.py` — **every 2min**, no_agent=true. Trails SL, auto-TP at $8, peak drawdown, daily loss limit
- `auto_scalper.py` — **every 3min**, no_agent=true. Opens trades at 4+/7 confluence
- `xauusd_monitor.py` — every 30min, alerts on price/RSI/AMD shifts
- `xauusd_analyzer.py` — daily 07:00 report
- All are watchdog pattern: silent when nothing to report, output only on alerts
