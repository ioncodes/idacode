import tornado.websocket
import os
import idaapi
import idacode_utils.dbg as dbg
import idacode_utils.hooks as hooks

def create_env():
    return {
        "dbg": dbg,
        "breakpoint": dbg.bp,
        "idacode": True
    }

class SocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("WebSocket opened")

    def on_message(self, message):
        print(message)
        script = message.decode("utf8")
        script_folder = os.path.dirname(script)
        env = create_env()
        hooks.set_script_folder(script_folder)
        
        print(f"Executing {script}")
        idaapi.execute_sync(
            lambda: idaapi.IDAPython_ExecScript(script, env),
            idaapi.MFF_WRITE
        )
        self.write_message(u"You said: " + message)

    def on_close(self):
        print("WebSocket closed")