import sys
import subprocess


class USBRelayBoard8(object):

    OFF = 0
    ON = 1

    def __init__(self, board_id: str = 'HW554'):
        self.board_id = board_id

    def set(self, channel: int, state: int):
        subprocess.run(f"sudo usbrelay {self.board_id}_{channel}={state}",
                       shell=True,
                       stdin=sys.stdin,
                       stdout=subprocess.DEVNULL,
                       stderr=sys.stderr)
