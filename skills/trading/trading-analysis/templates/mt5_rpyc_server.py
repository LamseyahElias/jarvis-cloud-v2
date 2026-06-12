"""
MT5 RPyC Server v3 — runs on Windows, bridges MetaTrader5 to WSL.
Compatible with RPyC 6.x. Returns plain dicts to avoid pickle errors.

Usage: python mt5_rpyc_server.py

Place at: C:\Users\<username>\mt5_rpyc_server.py
Start: python mt5_rpyc_server.py (or via PowerShell Start-Process from WSL)
"""
import rpyc
from rpyc.utils.server import ThreadedServer
import MetaTrader5 as mt5


class MT5Service(rpyc.Service):
    exposed_mt5 = mt5

    def on_connect(self, conn):
        print("[+] Client connected")
        conn._config["allow_all_attrs"] = True
        conn._config["allow_pickle"] = True
        conn._config["allow_public_attrs"] = True

    def on_disconnect(self, conn):
        print("[-] Client disconnected")

    def exposed_send_order(self, action, symbol, volume, order_type, price, sl, tp,
                           deviation, magic, comment, type_time, type_filling, position=None):
        """Execute order — returns plain dict to avoid RPyC pickle issues."""
        request = {
            "action": action, "symbol": symbol, "volume": volume, "type": order_type,
            "price": price, "sl": sl, "tp": tp, "deviation": deviation,
            "magic": magic, "comment": comment, "type_time": type_time,
            "type_filling": type_filling,
        }
        if position is not None:
            request["position"] = position
        print(f"[ORDER] {request}")
        result = mt5.order_send(request)
        if result:
            print(f"[ORDER] retcode={result.retcode} comment={result.comment}")
            return {
                "retcode": result.retcode, "deal": result.deal, "order": result.order,
                "volume": result.volume, "price": result.price, "bid": result.bid,
                "ask": result.ask, "comment": result.comment, "request_id": result.request_id,
            }
        else:
            err = mt5.last_error()
            print(f"[ORDER] Failed: {err}")
            return {"retcode": -1, "comment": str(err), "deal": 0, "order": 0}

    def exposed_get_positions(self, symbol=None):
        """Get open positions as plain dicts."""
        positions = mt5.positions_get(symbol=symbol) if symbol else mt5.positions_get()
        if not positions:
            return []
        return [{
            "ticket": p.ticket, "time": p.time, "type": p.type, "volume": p.volume,
            "price_open": p.price_open, "sl": p.sl, "tp": p.tp,
            "price_current": p.price_current, "profit": p.profit,
            "symbol": p.symbol, "comment": p.comment, "magic": p.magic,
        } for p in positions]


if __name__ == "__main__":
    HOST = "0.0.0.0"
    PORT = 18812
    print(f"MT5 RPyC Server v3 starting on {HOST}:{PORT}")
    if mt5.initialize():
        info = mt5.terminal_info()
        print(f"MT5 Terminal: {info.name if info else 'Unknown'}, Build {info.build if info else 'N/A'}")
        mt5.shutdown()
    else:
        print("WARNING: MT5 initialize() failed — is MT5 terminal running?")
    print("Press Ctrl+C to stop")
    server = ThreadedServer(MT5Service, hostname=HOST, port=PORT, protocol_config={
        "allow_all_attrs": True, "allow_pickle": True,
        "allow_public_attrs": True, "sync_request_timeout": 30,
    })
    server.start()
