import tornado.websocket, debugpy
import json
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
    debugpy.listen((settings.HOST, settings.DEBUG_PORT))
    print(f"IDACode debug server listening on {settings.HOST}:{settings.DEBUG_PORT}")

class SocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("WebSocket opened")

    def on_message(self, message):
        message = json.loads(message.decode("utf8"))
        
        if message["event"] == "set_workspace":
            path = message["path"]
            hooks.set_script_folder(path)
            start_debug_server()
        elif message["event"] == "execute_script":
            script = message["path"]
            env = create_env()
            print(f"Executing {script}")
            idaapi.execute_sync(
                lambda: idaapi.IDAPython_ExecScript(script, env),
                idaapi.MFF_WRITE
            )
        else:
            print(f"Invalid event {message['event']}")

    def on_close(self):
        print("WebSocket closed")