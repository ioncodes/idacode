import idaapi
import uuid

def safe_iteration(iterator):
    safe_iteration.egg = uuid.uuid4().hex
    safe_iteration.iteration_value = None

    def iteration_handler():
        try:
            safe_iteration.iteration_value = next(iterator)
        except StopIteration:
            safe_iteration.iteration_value = safe_iteration.egg
        return True

    while True:
        idaapi.execute_sync(iteration_handler, idaapi.MFF_WRITE)
        if safe_iteration.iteration_value == safe_iteration.egg:
            return
        yield safe_iteration.iteration_value