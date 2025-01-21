import sys, threading, subprocess, logging
import idacode_utils.settings as settings
try:
    import tornado, debugpy
except ImportError:
    print("[IDACode] Dependencies missing, run:\n  \"{}\" -m pip install --user debugpy tornado".format(settings.PYTHON))
    sys.exit()
import idaapi
from idacode_utils.socket_handler import SocketHandler

# Source: https://github.com/OALabs/hexcopy-ida/blob/8b0b2a3021d7dc9010c01821b65a80c47d491b61/hexcopy.py#L30
major, minor = map(int, idaapi.get_kernel_version().split("."))
using_ida7api = (major > 6)
using_pyqt5 = using_ida7api or (major == 6 and minor >= 9)

if using_pyqt5:
    import PyQt5.QtWidgets as QtWidgets
else:
    import PySide.QtGui as QtGui
    QtWidgets = QtGui

# Fix for https://github.com/tornadoweb/tornado/issues/2608
if sys.version_info >= (3, 4):
    import asyncio

def join_gui_thread(thread: threading.Thread, timeout=None):
    iterations = 0
    iteration_timeout = 0.1
    while True:
        if not thread.is_alive():
            return True
        thread.join(iteration_timeout)
        QtWidgets.QApplication.processEvents()
        if timeout is not None and iteration_timeout * iterations >= timeout:
            return False
        iterations += 1

class Server:
    def __init__(self):
        self.started = False
        self.server: tornado.httpserver.HTTPServer = None
        self.thread: threading.Thread = None

    def start(self):
        self.stop()
        self.thread = threading.Thread(target=self.server_thread)
        self.thread.start()
        self.started = True

    def stop(self):
        if not self.started:
            return

        if self.server is not None:
            self.io_loop.add_callback(self.server.stop)
            self.io_loop.add_callback(self.server.close_all_connections)
            self.io_loop.add_callback(self.io_loop.stop)

        if not join_gui_thread(self.thread, 1.0):
            print("[IDACode] Waiting for server to stop...")
            if not join_gui_thread(self.thread, 5.0):
                print("[IDACode] deadlock while stopping server, please report an issue!\n")
        self.thread = None
        self.server = None
        print("[IDACode] Server stopped")

    def server_thread(self):
        # Create a new event loop for the thread
        # https://github.com/tornadoweb/tornado/issues/2308#issuecomment-372582005
        loop = asyncio.new_event_loop()
        loop.set_debug(False)
        logging.getLogger("asyncio").setLevel(logging.CRITICAL)  # Remove some debug spam
        asyncio.set_event_loop(loop)

        # Before starting the event loop, instantiate a WebSocketClient and add a
        # callback to the event loop to start it. This way the first thing the
        # event loop does is to start the client.
        self.io_loop = tornado.ioloop.IOLoop.current()
        app = tornado.web.Application([
            (r"/ws", SocketHandler),
        ])
        self.server = tornado.httpserver.HTTPServer(app)
        print("[IDACode] Listening on {address}:{port}".format(address=settings.HOST, port=settings.PORT))
        self.server.listen(address=settings.HOST, port=settings.PORT)

        # Start the event loop.
        self.io_loop.start()

        # Signal that the service is finished
        self.started = False

def get_python_versions():
    settings_version = subprocess.check_output([settings.PYTHON, "-c", "import sys; print(sys.version + sys.platform)"])
    settings_version = settings_version.decode("utf-8", "ignore").strip()
    ida_version = "{}{}".format(sys.version, sys.platform)
    return (settings_version, ida_version)

class IDACode(idaapi.plugin_t):
    flags = idaapi.PLUGIN_KEEP
    comment = "IDACode"
    help = "IDACode"
    wanted_name = "IDACode"
    wanted_hotkey = "Ctrl-Shift-I"

    def init(self):
        settings_version, ida_version = get_python_versions()
        if settings_version != ida_version:
            print("[IDACode] settings.PYTHON version mismatch, aborting load:")
            print("[IDACode] IDA interpreter: {}".format(ida_version))
            print("[IDACode] settings.PYTHON: {}".format(settings_version))
            return idaapi.PLUGIN_SKIP

        self.server = Server()
        print("[IDACode] Plugin version 0.4.0")
        print("[IDACode] Plugin loaded, use Edit -> Plugins -> IDACode to start the server")
        return idaapi.PLUGIN_KEEP

    def run(self, args):
        self.server.start()

    def term(self):
        self.server.stop()