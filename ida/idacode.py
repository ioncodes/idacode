import socket
import threading
import inspect
import sys
import os
import idaapi
import debugpy

from idacode_utils.safe_idaapi import SafeIDAAPI
from idacode_utils.safe_idautils import SafeIDAUtils
from idacode_utils.safe_idc import SafeIDC
import idacode_utils.dbg as dbg

HOST = "127.0.0.1"
PORT = 7065
PYTHON = "C:\\Python37\\python37.exe"

getcwd_original = os.getcwd
script_folder = ""

def getcwd_hook():
    cwd = getcwd_original()
    global script_folder
    if cwd.lower() in script_folder.lower() and script_folder.lower() != cwd.lower():
        cwd = script_folder
    return cwd

def start_server():
    os.getcwd = getcwd_hook
    sys.executable = PYTHON
    debugpy.listen(7066)

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
            # TODO: try wrapping IDAPython_ExecScript in a safe handler instead
            global script_folder
            script_folder = os.path.dirname(script)
            idaapi.IDAPython_ExecScript(script, vars)

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