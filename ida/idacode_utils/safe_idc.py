import idc
import idaapi
import sys
from .utils import safe_iteration

class SafeIDC(object):
    def __getattribute__(self, name):
        value = None

        if hasattr(idc, name):
            value = getattr(idc, name)
        else:
            raise AttributeError(name)

        if hasattr(value, "__call__"):
            def call(*args, **kwargs):
                call.last_exception = None
                call.last_return = None

                def call_handler():
                    try:
                        call.last_return = value(*args, **kwargs)
                        return True
                    except:
                        _, exception, _ = sys.exc_info()
                        call.last_exception = exception
                        return False

                return_value = idaapi.execute_sync(
                    call_handler,
                    idaapi.MFF_WRITE
                )
                
                if return_value == False and call.last_exception != None:
                    print(f"Error: {call.last_exception}")

                if hasattr(call.last_return, "__iter__"):
                    # inspect.isgenerator(object)
                    call.last_return = safe_iteration(call.last_return)

                return call.last_return

            return call
        else:
            return value