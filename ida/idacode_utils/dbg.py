import debugpy
from debugpy.server import api

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