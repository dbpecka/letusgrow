import io
import time

import sys
import subprocess


class USBRelayBoard8(object):

    OFF = 0
    ON = 1

    def __init__(self, board_id: str = ''):
        self.board_id = board_id

    @staticmethod
    def set(self, channel: int, state: int):
        set_state = "on" if state == 1 else "off"
        subprocess.run(f"sainsmartrelay --{set_state} {channel}", shell=True, stdin=sys.stdin, stdout=subprocess.DEVNULL, stderr=sys.stderr)
        time.sleep(3)

    def get_all_states(self):
        states = dict()
        result = subprocess.run(f"sainsmartrelay --status all", shell=True, capture_output=True, text=True)
        for line in result.stdout.splitlines():
            try:
                line = line.strip()
                cs = line.split(':')[1].strip()
                states[line.split(':')[0]] = self.OFF if cs == 'OFF' else self.ON
            except Exception as ex:
                print(f"Error processing line '{line}': {str(ex)}")

        return states
