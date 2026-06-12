# MT5 RPyC Bridge — Architecture & Quirks

## Overview

MetaTrader5 Python package is Windows-only (.pyd binary). On WSL, we bridge via RPyC v6:

```
WSL (Ubuntu)                          Windows
────────────                          ────────
mt5_bridge.py ──► rpyc.connect() ──► mt5_rpyc_server.py ──► MetaTrader5 module
  (client)          172.26.128.1:18812    (server)              (native DLL)
```

## Critical: RPyC v6 Serialization

MT5 returns custom named-tuple types: `OrderSendResult`, `TradePosition`, `SymbolInfo`, `AccountInfo`, `Tick`.

These CANNOT be pickled over RPyC v6. `rpyc.utils.classic.obtain()` will fail with:
```
PicklingError: Can't pickle <class 'OrderSendResult'>: it's not found as builtins.OrderSendResult
```

**Solution:** The server converts all MT5 results to plain Python dicts BEFORE returning them:
- `exposed_send_order()` → returns `{"retcode": ..., "deal": ..., "order": ..., ...}`
- `exposed_get_positions()` → returns `[{"ticket": ..., "type": ..., "volume": ..., ...}]`

Objects that ARE safe to access via netrefs (no pickling needed):
- `mt5.initialize()`, `mt5.shutdown()` → return bool
- `mt5.symbol_info_tick()` → attributes accessed via netref work (tick.bid, tick.ask)
- `mt5.account_info()` → same (acc.balance, acc.equity)
- `mt5.copy_rates_from_pos()` → use `rpyc.utils.classic.obtain()` to get local numpy array, then wrap in DataFrame

## WSL → Windows Networking

- `localhost` / `127.0.0.1` does NOT work from WSL to Windows
- Use gateway IP: `ip route show default | awk '{print $3}'` → typically `172.26.128.1`
- DNS nameserver from `/etc/resolv.conf` (`10.255.255.254`) may NOT be the same as the gateway
- Test with: `rpyc.connect("172.26.128.1", 18812)`

## Server Restart Pattern

```bash
# From WSL — kill old, start new (minimized):
powershell.exe -Command "Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force; Start-Sleep 2; Start-Process python -ArgumentList 'C:\Users\USER\mt5_rpyc_server.py' -WindowStyle Minimized"

# Wait 5 seconds for server to initialize MT5, then test
sleep 5 && cd ~/trading/scripts && ~/finance_env/bin/python mt5_bridge.py
```

NOTE: `cmd.exe /c "start ..."` hangs from WSL. Always use PowerShell's `Start-Process`.

## Version Compatibility

- Windows: Python 3.14, MetaTrader5==5.0.5735, rpyc==6.0.2
- WSL: Python 3.14 (finance_env), rpyc==6.0.2
- mt5linux package (installed but NOT used) pins rpyc==5.2.3 — ignore the warning
- We use our own mt5_bridge.py instead of mt5linux for full control
