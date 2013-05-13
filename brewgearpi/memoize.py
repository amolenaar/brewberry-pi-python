
import time

def memoize(timeout=None):
    def function_decorator(func):
        mem = {}
        def wrapper(*args):
            ts = time.time()
            try:
                last_ts, result = mem[args]
            except KeyError:
                result = func(*args)
                mem[args] = (ts, result)
            else:
                if timeout and ts - last_ts > timeout:
                    result = func(*args)
                    mem[args] = (ts, result)
            return result
        return wrapper
    return function_decorator

# vim: sw=4:et:ai
