import socket
import threading
"""from gevent import monkey, sleep, socket
monkey.patch_all(thread=False)
from gevent.server import StreamServer"""

from idc import *
import random
import idaapi
import idc

HOST = "127.0.0.1"
PORT = 10100

# https://github.com/vrtadmin/FIRST-plugin-ida/blob/6c2f7d0b6f817cc8e22ed6aa0d7e9814c1100aeb/first_plugin_ida/first.py

class SafeIDC(object):
    def __getattribute__(self, name):
        value = None

        if hasattr(idc, name):
            value = getattr(idc, name)

        if hasattr(value, "__call__"):
            def call(*args, **kwargs):
                holder = [ None ]

                def trampoline():
                    holder[0] = value(*args, **kwargs)
                    return 1

                idaapi.execute_sync(trampoline, idaapi.MFF_WRITE)
                return holder[0]

            return call
        else:
            return value

class SafeIDAAPI(object):
    def __getattribute__(self, name):
        value = None

        if hasattr(idaapi, name):
            value = getattr(idaapi, name)

        if hasattr(value, "__call__"):
            def call(*args, **kwargs):
                holder = [ None ]

                def trampoline():
                    holder[0] = value(*args, **kwargs)
                    return 1

                idaapi.execute_sync(trampoline, idaapi.MFF_WRITE)
                return holder[0]

            return call
        else:
            return value

def safe_generator(iterator):
    sentinel = f"[1st] Sentinel {random.randint(0, 65535)}"

    holder = [ sentinel ]

    def trampoline():
        try:
            holder[0] = next(iterator)
        except StopIteration:
            holder[0] = sentinel
        return 1

    while True:
        idaapi.execute_sync(trampoline, idaapi.MFF_WRITE)
        if holder[0] == sentinel:
            return
        yield holder[0]

def start_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen(5)
    print(f"IDACode listening on {HOST}:{PORT}")

    while True:
        io, _ = sock.accept()
        script = io.recv(256) # MAX_PATH
        io.close()

        if script and len(script) > 0:
            script = script.decode("utf8")
            print(f"Executing {script}")
            vars = {
                "idaapi": SafeIDAAPI(),
                "idc": SafeIDC(),
                "vscode_ida": True
            }
            idaapi.IDAPython_ExecScript(script, vars)

"""
def start_server_gevent(socket, address):
    while True:
        data = socket.recv(256) # MAX_PATH

        if data and len(data) > 0:
            script = data.decode("utf8")
            print(f"Executing {script}")
            env = SafeIDA()
            vars = {
                "idaapi": env,
                "idc": env
            }
            idaapi.IDAPython_ExecScript(script, globals()) # TODO: remove global

def stuff():
    print(f"IDACode listening on {HOST}:{PORT}")
    server = StreamServer(('127.0.0.1', PORT), start_server_gevent)
    server.serve_forever()
"""

class VSCodeServer(idaapi.plugin_t):
    def __init__(self):
        self.flags = idaapi.PLUGIN_UNL
        self.comment = "VSCode Server"
        self.help = "VSCode Server"
        self.wanted_name = "Toggle VSCode Server"
        self.wanted_hotkey = ""

    def init(self):
        return idaapi.PLUGIN_OK

    def run(self, args):
        thread = threading.Thread(target=start_server)
        thread.daemon = True
        thread.start()
        """thread = threading.Thread(target=stuff)
        thread.daemon = True
        thread.start()"""
        

    def term(self):
        pass

def PLUGIN_ENTRY():
    return VSCodeServer()