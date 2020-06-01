import socket, sys, os, threading, inspect, asyncio
import tornado, debugpy
import idaapi
import idacode_utils.dbg as dbg
import idacode_utils.hooks as hooks
import idacode_utils.settings as settings
from idacode_utils.socket_handler import SocketHandler

def setup_patches():
    hooks.install()
    sys.executable = settings.PYTHON

def create_socket_handler():
    asyncio.set_event_loop(asyncio.new_event_loop())
    app = tornado.web.Application([
        (r"/ws", SocketHandler),
    ])
    server = tornado.httpserver.HTTPServer(app)
    print(f"IDACode listening on {settings.HOST}:{settings.PORT}")
    server.listen(address=settings.HOST, port=settings.PORT)

def start_server():
    setup_patches()
    create_socket_handler()
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