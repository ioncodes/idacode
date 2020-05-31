import socket, sys, os, threading, inspect, asyncio
import debugpy, tornado
import idaapi
import idacode_utils.dbg as dbg
import idacode_utils.hooks as hooks
from idacode_utils.socket_handler import SocketHandler

"""
TODO:
* Implement event system
  -> VS Code send enable to IDA with workspace 
     path so debugger can launch accordingly
"""

HOST = "127.0.0.1"
PORT = 7065
DEBUG_PORT = 7066
PYTHON = "C:\\Python37\\python37.exe"

def setup_patches():
    hooks.install()
    sys.executable = PYTHON

def start_debug_server():
    debugpy.listen((HOST, DEBUG_PORT))
    print(f"IDACode debug server listening on {HOST}:{DEBUG_PORT}")

def create_socket_handler():
    asyncio.set_event_loop(asyncio.new_event_loop())
    app = tornado.web.Application([
        (r"/ws", SocketHandler),
    ])
    server = tornado.httpserver.HTTPServer(app)
    print(f"IDACode listening on {HOST}:{PORT}")
    server.listen(address=HOST, port=PORT)

def start_server():
    setup_patches()
    create_socket_handler()
    start_debug_server()
    tornado.ioloop.IOLoop.instance().start()

class IDACode(idaapi.plugin_t):
    def __init__(self):
        self.flags = idaapi.PLUGIN_UNL
        self.comment = "IDACode"
        self.help = "IDACode"
        self.wanted_name = "Start IDACode"
        self.wanted_hotkey = ""

    def init(self):
        return idaapi.PLUGIN_OK

    def run(self, args):
        thread = threading.Thread(target=start_server)
        thread.daemon = True
        thread.start()

    def term(self):
        pass

def PLUGIN_ENTRY():
    return IDACode()