import sys
import subprocess


class USBRelayBoard8(object):

    OFF = 0
    ON = 1

    def __init__(self, board_id: str = ''):
        self.board_id = board_id

    def set(self, channel: int, state: int):
        set_state = "on" if state == 1 else "off"
        subprocess.run(f"sudo sainsmartrelay --{set_state} {channel}", shell=True, stdin=sys.stdin, stdout=subprocess.DEVNULL, stderr=sys.stderr)
        #subprocess.run(f"sudo usbrelay {self.board_id}_{channel}={state}",
        #               shell=True,
        #               stdin=sys.stdin,
        #               stdout=subprocess.DEVNULL,
        #               stderr=sys.stderr)

