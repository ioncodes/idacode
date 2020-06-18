import socket, sys, os, threading, inspect, subprocess
try:
    import tornado, debugpy
except ImportError:
    print("[IDACode] Dependencies missing, run: python -m pip install --user debugpy tornado")
    sys.exit()
import idaapi
import idacode_utils.dbg as dbg
import idacode_utils.hooks as hooks
import idacode_utils.settings as settings
from idacode_utils.socket_handler import SocketHandler

VERSION = "0.1.3"
initialized = False

def setup_patches():
    hooks.install()
    sys.executable = settings.PYTHON

def create_socket_handler():
    if sys.version_info >= (3, 4):
        import asyncio
        asyncio.set_event_loop(asyncio.new_event_loop())
    app = tornado.web.Application([
        (r"/ws", SocketHandler),
    ])
    server = tornado.httpserver.HTTPServer(app)
    print("[IDACode] Listening on {address}:{port}".format(address=settings.HOST, port=settings.PORT))
    server.listen(address=settings.HOST, port=settings.PORT)

def start_server():
    setup_patches()
    create_socket_handler()
    tornado.ioloop.IOLoop.current().start()

def get_python_versions():
    settings_version = subprocess.check_output([settings.PYTHON, "-c", "import sys; print(sys.version + sys.platform)"])
    settings_version = settings_version.decode("utf-8", "ignore").strip()
    ida_version = "{}{}".format(sys.version, sys.platform)
    return (settings_version, ida_version)

class IDACode(idaapi.plugin_t):
    def __init__(self):
        self.flags = idaapi.PLUGIN_UNL
        self.comment = "IDACode"
        self.help = "IDACode"
        self.wanted_name = "IDACode"
        self.wanted_hotkey = ""

    def init(self):
        global initialized
        if not initialized:
            initialized = True
            if os.path.isfile(settings.PYTHON):
                settings_version, ida_version = get_python_versions()
                if settings_version != ida_version:
                    print("[IDACode] settings.PYTHON version mismatch, aborting load:")
                    print("[IDACode] IDA interpreter: {}".format(ida_version))
                    print("[IDACode] settings.PYTHON: {}".format(settings_version))
                    return idaapi.PLUGIN_SKIP
            else:
                print("[IDACode] settings.PYTHON ({}) does not exist, aborting load".format(settings.PYTHON))
                print("[IDACode] To fix this issue, modify idacode_utils/settings.py to point to the python executable")
                return idaapi.PLUGIN_SKIP
            print("[IDACode] Plugin version {}".format(VERSION))
            print("[IDACode] Plugin loaded, use Edit -> Plugins -> IDACode to start the server")
        return idaapi.PLUGIN_OK

    def run(self, args):
        thread = threading.Thread(target=start_server)
        thread.daemon = True
        thread.start()

    def term(self):
        pass