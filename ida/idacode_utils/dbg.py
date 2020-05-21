import debugpy
#import socket
from debugpy.server import api
#from debugpy.common import sockets

# this requires a modification to listen() in api.py of debug.py
# by default it takes the running python binary from sys.executable
# which resolves to IDA in this case. it has to be monkey patched or 
# permantly patched in the file
# additionally this requires a os.chdir() as IDA changes the current
# dir before executing the script

"""
original_create_server = None
original_socket = None

def create_server_hook(host, port=0, backlog=socket.SOMAXCONN, timeout=None):
    global original_create_server
    global original_socket

    original_socket = original_create_server(host, port, backlog, timeout)
    return original_socket
"""

def attach(port):
    """global original_create_server
    global original_socket"""

    # doesnt work very well
    #original_create_server = sockets.create_server
    #sockets.create_server = create_server_hook
    debugpy.listen(port)
    debugpy.wait_for_client()

"""
def detach():
    global original_socket

    sockets.shut_down(original_socket)
    sockets.create_server = original_create_server
"""

def bp(*args):
    condition = True
    message = ""
    for arg in args:
        if type(arg) is bool:
            condition = arg
            break
    for arg in args:
        if type(arg) is str:
            message = arg
            break
    if condition:
        if message:
            print(message)
        api.breakpoint()