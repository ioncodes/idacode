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
DEBUG_PORT = 7066
PYTHON = "C:\\Python37\\python37.exe"

getcwd_original = os.getcwd
script_folder = ""

def getcwd_hook():
    cwd = getcwd_original()
    global script_folder
    if cwd.lower() in script_folder.lower() and script_folder.lower() != cwd.lower():
        cwd = script_folder
    return cwd

def setup_patches():
    os.getcwd = getcwd_hook
    sys.executable = PYTHON

def start_debug_server():
    debugpy.listen(DEBUG_PORT)
    print(f"IDACode debug server listening on {HOST}:{DEBUG_PORT}")

def start_socket_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen(5)
    print(f"IDACode listening on {HOST}:{PORT}")
    return sock

def create_env():
    return {
        "idaapi": SafeIDAAPI(),
        "idc": SafeIDC(),
        "idautils": SafeIDAUtils(),
        "dbg": dbg,
        "idacode": True
    }

def handle_connection(script):
    global script_folder
    
    if script and len(script) > 0:
        script = script.decode("utf8")
        script_folder = os.path.dirname(script)
        env = create_env()
        print(f"Executing {script}")
        # TODO: try wrapping IDAPython_ExecScript in a safe handler instead
        idaapi.IDAPython_ExecScript(script, env)

def start_server():
    setup_patches()
    sock = start_socket_server()
    start_debug_server()

    while True:
        io, _ = sock.accept()
        data = io.recv(256) # MAX_PATH
        io.close()

        handle_connection(data)


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