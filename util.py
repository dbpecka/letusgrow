import sys
import datetime


def log(m: str):
    print(f"[{datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')}] [App=LetUsGrow] {m}")
    sys.stdout.flush()

