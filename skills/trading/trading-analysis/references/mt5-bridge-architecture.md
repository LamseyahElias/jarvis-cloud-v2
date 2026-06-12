# MT5 Bridge Architecture

## Data Flow

```
xauusd_analyzer.py
  └── data_provider.py  (get_data)
        ├── [1] MT5: mt5_bridge.py → RPyC → Windows mt5_rpyc_server.py → MetaTrader5
        └── [2] Fallback: yfinance (GC=F ticker)
```

## mt5_bridge.py — Key Design Decisions

- **Custom RPyC client** (not mt5linux's high-level API) — avoids version-pinning issues and gives us control over protocol config
- **MT5Bridge class** exposes methods matching the official MetaTrader5 API: `initialize()`, `shutdown()`, `symbol_info_tick()`, `copy_rates_from_pos()`, `copy_rates_range()`, `order_send()`, etc.
- Remote numpy arrays are materialized locally via `rpyc.utils.classic.obtain(rates)` → pandas DataFrame on the WSL side. Direct iteration of netrefs (`[tuple(r) for r in rates]`) fails with type conversion errors on RPyC v6.
- Column renaming (`time→Date`, `open→Open`, etc.) happens in the bridge so downstream code doesn't care about data source
- Includes `quick_test()` function — run `python mt5_bridge.py` standalone to validate the connection

## data_provider.py — Dual Source

- `get_data(timeframe_key, use_mt5=True)` → returns `(DataFrame, source_string)`
- Tries MT5 first, returns "MT5" as source; on any failure, falls back to yfinance and returns "yfinance"
- Timeframe mapping: "1m", "5m", "15m", "30m", "1h", "4h", "1d" all supported for MT5; yfinance uses its own period/interval params
- Analyzer shows which source was used in the report header

## mt5_rpyc_server.py — Windows Server (RPyC v6)

- Custom `MT5Service` class exposes MT5 as a **class attribute**: `exposed_mt5 = mt5`
- This is the RPyC v6 pattern — v5 used `exposed_get_module()` method which no longer works in v6
- Protocol config: `allow_all_attrs`, `allow_pickle`, `allow_public_attrs` all True
- Validates MT5 connection on startup — prints terminal info or warning
- Port 18812, must bind to `0.0.0.0` (NOT `127.0.0.1` — see pitfalls)
- **Bind address history:** Originally hardcoded to `127.0.0.1`, which prevented WSL from connecting. Patched to `0.0.0.0` in session 2026-06-10. If the server file resets to `127.0.0.1` after updates, re-patch.

## WSL → Windows Networking

- **`localhost` does NOT work** from WSL to reach Windows services
- Use the WSL gateway IP: `ip route show default | awk '{print $3}'` (typically `172.26.x.1`)
- **IP is dynamic** — it can change between WSL restarts or network changes. Always discover dynamically rather than hardcoding.
- The `mt5_bridge.py` default host was originally hardcoded to a specific IP; now use dynamic detection.
- `/etc/resolv.conf` nameserver may show a different IP (e.g. `10.255.255.254`) — this is DNS, not the gateway

## RPyC v6 Netref Serialization

- Remote numpy structured arrays (from `copy_rates_from_pos`) are RPyC netrefs, not local objects
- Iterating them with `[tuple(r) for r in rates]` causes type conversion errors
- **Fix:** Use `rpyc.utils.classic.obtain(rates)` to materialize the entire array locally before passing to pandas
- The `socket.setdefaulttimeout(5)` in data_provider prevents hanging when the RPyC server is down

## Starting/Stopping the Windows Server

From WSL:

```bash
# Start as hidden background process
powershell.exe -Command "Start-Process -WindowStyle Hidden -FilePath 'C:\Users\USER\AppData\Local\Python\pythoncore-3.14-64\python.exe' -ArgumentList 'C:\Users\USER\mt5_rpyc_server.py'"

# Kill stale Python processes
taskkill.exe /F /IM python.exe

# Verify server is listening (from Windows side)
# powershell.exe "netstat -ano | findstr :18812"
```

## Verifying the Bridge

```python
import rpyc
c = rpyc.connect(gateway_ip, 18812, config={'sync_request_timeout': 10})
mt5 = c.root.exposed_mt5
mt5.initialize()
info = mt5.account_info()
print(f"Bal: {info.balance}  Eq: {info.equity}")
c.close()
```

## Potential Issues

- **rpyc version mismatch**: Windows has v6, WSL should also use v6 (`pip install "rpyc>=6.0"`). The mt5linux package pins rpyc==5.2.3 — ignore the pip dependency conflict warning, we use the custom bridge not mt5linux's API.
- **MT5 symbol names**: ICMarkets uses "XAUUSD" (verify in MT5 terminal Market Watch). Some brokers use "GOLD" or "XAUUSDm".
- **Firewall**: Windows firewall may block port 18812. Add exception if connection fails from WSL.
- **Stale processes**: If a previous server instance is still running on port 18812, the new one will fail with "Only one usage of each socket address". Kill ALL `python.exe` processes and restart.
- **Connection timeout**: If the bridge connection times out, the server is likely not running on Windows. Start it first, then try again.
