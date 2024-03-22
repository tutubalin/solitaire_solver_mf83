from contextlib import contextmanager
import time
import sys

@contextmanager
def profile(comment):    
    print(comment, end = '', file=sys.stderr)
    start_time = time.time_ns()
    try:
        yield
    finally:
        time_in_ms = (time.time_ns() - start_time)/1000000
        print(f' Done in {time_in_ms}ms', file=sys.stderr)