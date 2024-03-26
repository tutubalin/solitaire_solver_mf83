from contextlib import contextmanager
import time
import sys

@contextmanager
def profile(comment):    
    print(comment, end = '', file=sys.stderr, flush=True)
    start_time = time.time_ns()
    try:
        yield
    finally:
        time_in_ms = (time.time_ns() - start_time)/1000000
        print(f'\033[1;32m Done\033[0m in \033[1;33m{time_in_ms:.2f}\033[0m ms', file=sys.stderr, flush=True)