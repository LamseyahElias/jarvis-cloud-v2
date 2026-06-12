"""
MT5 RPyC Server v2 — runs on Windows, bridges MetaTrader5 to WSL.
Compatible with RPyC 6.x.

Prerequisites (Windows):
  pip install MetaTrader5 rpyc

Usage:
  python mt5_rpyc_server.py

Then from WSL, run:
  ~/finance_env/bin/python ~/trading/scripts/mt5_bridge.py
"""
import rpyc
from rpyc.utils.server import ThreadedServer
import MetaTrader5 as mt5


class MT5Service(rpyc.Service):
    # RPyC v6: expose MT5 module as a class attribute (not via method)
    # Client accesses as: conn.root.exposed_mt5
    exposed_mt5 = mt5

    def on_connect(self, conn):
        print("[+] Client connected")
        conn._config["allow_all_attrs"] = True
        conn._config["allow_pickle"] = True
        conn._config["allow_public_attrs"] = True

    def on_disconnect(self, conn):
        print("[-] Client disconnected")


if __name__ == "__main__":
    HOST = "0.0.0.0"
    PORT = 18812
    print(f"MT5 RPyC Server starting on {HOST}:{PORT}")

    if mt5.initialize():
        info = mt5.terminal_info()
        print(f"MT5 Terminal: {info.name if info else 'Unknown'}")
        print(f"MT5 Connected: Build {info.build if info else 'N/A'}")
        mt5.shutdown()
    else:
        print("WARNING: MT5 initialize() failed — is MT5 terminal running?")

    print("Press Ctrl+C to stop")
    server = ThreadedServer(
        MT5Service,
        hostname=HOST,
        port=PORT,
        protocol_config={
            "allow_all_attrs": True,
            "allow_pickle": True,
            "allow_public_attrs": True,
            "sync_request_timeout": 30,
        },
    )
    server.start()
