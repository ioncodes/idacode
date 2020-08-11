import tornado.websocket, debugpy
import json, tempfile
import idaapi
import idacode_utils.dbg as dbg
import idacode_utils.hooks as hooks
import idacode_utils.settings as settings

def create_env():
    return {
        "dbg": dbg,
        "breakpoint": dbg.bp,
        "idacode": True,
        "__name__": "__main__"
    }

def start_debug_server():
    if settings.LOGGING:
        tmp_path = tempfile.gettempdir()
        debugpy.log_to(tmp_path)
        print("[IDACode] Logging to {} with pattern debugpy.*.log".format(tmp_path))
    debugpy.listen((settings.HOST, settings.DEBUG_PORT))
    print("[IDACode] IDACode debug server listening on {address}:{port}".format(address=settings.HOST, port=settings.DEBUG_PORT))

class SocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("[IDACode] Client connected")

    def on_message(self, message):
        message = json.loads(message.decode("utf8"))
        
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