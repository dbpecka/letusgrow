import datetime


def log(m: str):
    print(f"[{datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}]  {m}")
