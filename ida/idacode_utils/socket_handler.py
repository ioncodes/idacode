import tornado.websocket, debugpy
import json, tempfile
import idaapi
import idacode_utils.dbg as dbg
import idacode_utils.hooks as hooks
import idacode_utils.settings as settings

def create_env():
    return {
        "dbg": dbg,
        "__idacode__": True,
        "__name__": "__main__"
    }

debugpy_host = ""
debugpy_port = 0

def start_debug_server():
    # At most one instance of debugpy can ever be created per process.
    # Reference: https://github.com/microsoft/debugpy/issues/297
    global debugpy_host, debugpy_port
    if debugpy_port and debugpy_port:
        print("[IDACode] debugpy server is already listening on {}:{}".format(debugpy_host, debugpy_port))
        return

    # Install hook for os.getcwd
    hooks.install()

    # Start debugpy server
    if settings.LOGGING:
        tmp_path = tempfile.gettempdir()
        debugpy.log_to(tmp_path)
        print("[IDACode] Logging to {} with pattern debugpy.*.log".format(tmp_path))
    debugpy.configure(python=settings.PYTHON)
    debugpy_host, debugpy_port = debugpy.listen((settings.HOST, settings.DEBUG_PORT))
    print("[IDACode] Started debugpy server on {}:{}".format(debugpy_host, debugpy_port))

class SocketHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        # NOTE: This is called when connecting from a browser
        return settings.ALLOW_UNSAFE_ORIGIN

    def open(self):
        print("[IDACode] Client connected")

    def on_message(self, message):
        if not isinstance(message, str):
            message = message.decode("utf-8")
        message = json.loads(message)

        if message["event"] == "set_workspace":
            path = message["path"]
            hooks.set_script_folder(path)
            print("[IDACode] Set workspace folder to {}".format(path))
        elif message["event"] == "attach_debugger":
            start_debug_server()
            self.write_message({
                "event": "debugger_ready"
            })
        elif message["event"] == "execute_script":
            script = message["path"]
            env = create_env()
            print("[IDACode] Executing {}".format(script))
            idaapi.execute_sync(
                lambda: idaapi.IDAPython_ExecScript(script, env),
                idaapi.MFF_WRITE
            )
        else:
            print("[IDACode] Invalid event {}".format(message['event']))

    def on_close(self):
        print("[IDACode] Client disconnected")