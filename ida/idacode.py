import socket
import threading
import inspect
import sys
import os
import idaapi

from idacode_utils.safe_idaapi import SafeIDAAPI
from idacode_utils.safe_idautils import SafeIDAUtils
from idacode_utils.safe_idc import SafeIDC
import idacode_utils.dbg as dbg

HOST = "127.0.0.1"
PORT = 10100
PYTHON = "C:\\Python37\\python37.exe"

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
                "idautils": SafeIDAUtils(),
                "dbg": dbg,
                "idacode": True
            }
            old = sys.executable
            sys.executable = PYTHON
            new_cwd = os.path.dirname(script)
            old_cwd = os.getcwd()
            os.chdir(new_cwd)
            # TODO: try wrapping IDAPython_ExecScript in a safe handler instead
            # TODO: try attaching debugger through the plugin -> doesn't work
            idaapi.IDAPython_ExecScript(script, vars)
            os.chdir(old_cwd)
            sys.executable = old

class VSCodeServer(idaapi.plugin_t):
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
    return VSCodeServer()