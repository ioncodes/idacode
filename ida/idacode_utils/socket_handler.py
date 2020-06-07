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
        "idacode": True
    }

def start_debug_server():
    if settings.LOGGING:
        tmp_path = tempfile.gettempdir()
        debugpy.log_to(tmp_path)
        print(f"[IDACode] Logging to {tmp_path} with pattern debugpy.*.log")
    debugpy.listen((settings.HOST, settings.DEBUG_PORT))
    print(f"[IDACode] IDACode debug server listening on {settings.HOST}:{settings.DEBUG_PORT}")

class SocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("[IDACode] Client connected")

    def on_message(self, message):
        message = json.loads(message.decode("utf8"))
        
        if message["event"] == "set_workspace":
            path = message["path"]
            hooks.set_script_folder(path)
            print(f"[IDACode] Set workspace folder to {path}")
        elif message["event"] == "attach_debugger":
            start_debug_server()
            self.write_message({
                "event": "debugger_ready"
            })
        elif message["event"] == "execute_script":
            script = message["path"]
            env = create_env()
            print(f"[IDACode] Executing {script}")
            idaapi.execute_sync(
                lambda: idaapi.IDAPython_ExecScript(script, env),
                idaapi.MFF_WRITE
            )
        else:
            print(f"[IDACode] Invalid event {message['event']}")

    def on_close(self):
        print("[IDACode] Client disconnected")