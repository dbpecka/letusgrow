import serial
import time


class USBRelayBoard8(object):

    OFF = 0
    ON = 1
    GLOBAL_CHANNEL = 8

    def __init__(self, com_port: str = 'COM13', baud_rate: int = 9600):
        self.channels = [
            [bytearray([0xff, 0x01, 0x00]), bytearray([0xff, 0x01, 0x01])],  # channel-0
            [bytearray([0xff, 0x02, 0x00]), bytearray([0xff, 0x02, 0x02])],  # channel-1
            [bytearray([0xff, 0x03, 0x00]), bytearray([0xff, 0x03, 0x03])],  # channel-2
            [bytearray([0xff, 0x04, 0x00]), bytearray([0xff, 0x04, 0x04])],  # channel-3
            [bytearray([0xff, 0x05, 0x00]), bytearray([0xff, 0x05, 0x05])],  # channel-4
            [bytearray([0xff, 0x06, 0x00]), bytearray([0xff, 0x06, 0x06])],  # channel-5
            [bytearray([0xff, 0x07, 0x00]), bytearray([0xff, 0x07, 0x07])],  # channel-6
            [bytearray([0xff, 0x08, 0x00]), bytearray([0xff, 0x08, 0x08])],  # channel-7
            [bytearray([0x00]), bytearray([0xff])],  # all channels
        ]

        self.serial_port = serial.Serial(com_port, baud_rate)

    def get_bit_mask(self, channels: list):
        mask = 0x00
        for value in self.channels:
            mask |= value
        return bytearray(mask)

    def set(self, channel: int, state: int):
        with self.serial_port as port:
            port.write(self.channels[channel][state])
            port.flushOutput()
