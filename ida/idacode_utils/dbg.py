import debugpy
from debugpy.server import api

# this requires a modification to listen() in api.py of debug.py
# by default it takes the running python binary from sys.executable
# which resolves to IDA in this case. it has to be monkey patched or 
# permantly patched in the file
# additionally this requires a os.chdir() as IDA changes the current
# dir before executing the script

def listen(port):
    debugpy.listen(port)
    debugpy.wait_for_client()

def bp(msg=None, condition=None):
    if msg != None:
        print(msg)
    return api.breakpoint()
