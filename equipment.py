import os
import io
import sys
import time
from enum import Enum

from util import log
from adc import read_adc
from drivers.USBRelay import USBRelayBoard8
from atlas_i2c import atlas_i2c
import configuration


class USBRelayDrivenEquipment(object):
    OFF = 0
    OPEN = 0

    ON = 1 
    CLOSED = 1

    def __init__(self, usb_relay: USBRelayBoard8, channel: int, default_state=OFF, name: str = 'Unnamed'):
        self.name = name
        self.usb_relay = usb_relay
        self.channel = channel
        log(f"Event=RelayMap, "
            f"Channel={channel}, "
            f"DeviceType={type(self).__name__}, "
            f"State={default_state}, "
            f"Name={self.name}")
        self.set(default_state)
        self.last_state_set = default_state

    def set(self, state: int):
        self.usb_relay.set(self.channel, state)
        self.last_state_set = state
        log(f"Event=StateSet, "
            f"_{self.name}={'On' if state == USBRelayDrivenEquipment.ON else 'Off'}, "
            f"Name={self.name}, "
            f"Type=USBRelayDrivenEquipment, "
            f"SelfType={type(self).__name__}, "
            f"Channel={self.channel}, "
            f"State={'ON/CLOSED' if state == USBRelayDrivenEquipment.ON else 'OFF/OPEN'}")

    def open_off(self):
        self.set(USBRelayDrivenEquipment.OFF)

    def close_on(self):
        self.set(USBRelayDrivenEquipment.ON)

    def toggle(self):
        self.set(self.last_state_set ^ 1)


class Pump(USBRelayDrivenEquipment):
    def on(self):
        self.close_on()

    def off(self):
        self.open_off()


class Valve(USBRelayDrivenEquipment):
    def open(self):
        self.open_off()

    def close(self):
        self.close_on()


class DosingPump(Pump):
    def dose(self, amount=None):
        log(f"Event=Dose, "
            f"DeviceType={type(self).__name__}, "
            f"Channel={self.channel}, "
            f"Amount={amount}, "
            f"AmountUnits=seconds, "
            f"Name={self.name}")
        self.on()
        time.sleep(5)
        self.off()


class Light(USBRelayDrivenEquipment):
    def on(self):
        self.close_on()

    def off(self):
        self.open_off()


class PHSensor(object):
    def __init__(self, i2c_address=0x63):
        self.device = atlas_i2c.AtlasI2C()
        self.device.set_i2c_address(i2c_address)

    def read_ph(self):
        result = self.device.query("R", processing_delay=1500)
        if result.status_code == 1:
            log(f"Event=ReadPh, PhData={result.data}")
            return result.data
        else:
            log(f"Event=ReadPh, StatusCode={result.status_code}, Data={result.data}")
            return False


class LetUsGrowTower(object):
    def __init__(self, usb_relay,
                 relay_channel_lights=7,
                 relay_channel_watering_pump=8,
                 relay_channel_transfer_pump=4,
                 relay_channel_nutrient_dosing_pump=3,
                 relay_channel_ph_up_dosing_pump=5,
                 relay_channel_ph_down_dosing_pump=6,
                 relay_channel_transfer_pump_out_valve=2,
                 relay_channel_transfer_pump_mix_valve=1):

        self.usb_relay = usb_relay
        self.ph_sensor = PHSensor()

        self.lights = Light(usb_relay, relay_channel_lights, USBRelayDrivenEquipment.OFF, name='Lights')
        self.watering_pump = Pump(usb_relay, relay_channel_watering_pump, name='WateringPump')

        self.transfer_pump = Pump(usb_relay, relay_channel_transfer_pump, name='TransferPump')
        self.transfer_pump_out_valve = Valve(usb_relay, relay_channel_transfer_pump_out_valve, name='TransferPumpValve')
        self.transfer_pump_mix_valve = Valve(usb_relay, relay_channel_transfer_pump_mix_valve, name='MixingPumpValve')

        self.nutrient_dosing_pump = Pump(usb_relay, relay_channel_nutrient_dosing_pump, name='NutrientDosingPump')
        self.ph_up_dosing_pump = Pump(usb_relay, relay_channel_ph_up_dosing_pump, name='PhUpDosingPump')
        self.ph_down_dosing_pump = Pump(usb_relay, relay_channel_ph_down_dosing_pump, name='PhDownDosingPump')

    def state_audit(self):
        actual_relay_states = self.usb_relay.get_all_states()
        log(actual_relay_states)

        for device in [self.lights,
                       self.watering_pump,
                       self.transfer_pump,
                       self.transfer_pump_out_valve,
                       self.transfer_pump_mix_valve,
                       self.nutrient_dosing_pump,
                       self.ph_up_dosing_pump,
                       self.ph_down_dosing_pump]:
            if device.last_state_set != actual_relay_states[str(device.channel)]:
                log(f"Device state mismatch: {device.name}({device.channel}) is {actual_relay_states[str(device.channel)]} but should be {device.last_state_set}")

    def power_down(self):
        log(f"Event=TowerPowerDown")
        self.lights.off()
        self.watering_pump.off()
        self.transfer_pump.off()
        self.transfer_pump_mix_valve.close()
        self.transfer_pump_out_valve.close()
        self.nutrient_dosing_pump.off()
        self.ph_up_dosing_pump.off()
        self.ph_down_dosing_pump.off()

    def empty_tank(self):
        log(f"Event=EmptyingTank(Disabled), "
            f"Critical=True")
        # # first, turn off light and watering pump while we exchange water
        # self.watering_pump.off()
        # self.lights.off()
        #
        # # open the evac valve and start pumping
        # self.transfer_pump_mix_valve.close()
        # self.transfer_pump_out_valve.open()
        # self.transfer_pump.on()

        # todo: when the water is emptied (level is 0), stop
        # todo: wait until finished/emptied?

    def mix_tank(self):
        log(f"Event=MixingTank(Disabled)")
        # self.transfer_pump_out_valve.close()
        # self.transfer_pump_mix_valve.open()
        # time.sleep(configuration.VALVE_EXERCISE_TIME_SECS)
        # # todo: beep, alarm, or request button/hardware confirmation?
        # self.transfer_pump.on()
        # time.sleep(configuration.MIX_RUN_TIME_SECS)
        # self.transfer_pump.off()
        # self.transfer_pump_mix_valve.close()

    def reduce_ph(self):
        log(f"Event=ReducingPh")
        self.ph_down_dosing_pump.on()
        time.sleep(configuration.PH_ADJUST_DOSE_RUN_TIME_SECS)
        self.ph_down_dosing_pump.off()
        self.mix_tank()

    def increase_ph(self):
        log(f"Event=IncreasingPh")
        self.ph_up_dosing_pump.on()
        time.sleep(configuration.PH_ADJUST_DOSE_RUN_TIME_SECS)
        self.ph_up_dosing_pump.off()
        self.mix_tank()

    def evaluate_chemistry(self):
        log(f"Event=EvaluatingChemistry")

        # make sure pump is stopped so that the water can settle for a more accurate reading
        last_pump_state = self.watering_pump.last_state_set
        self.watering_pump.off()
        time.sleep(10)

        # read the ph
        ph = float(self.ph_sensor.read_ph())
        time.sleep(5)

        # set the pump state to whatever it was before
        self.watering_pump.set(last_pump_state)

        if 0 < ph < configuration.PH_LOW_LEVEL:
            self.increase_ph()

        if configuration.PH_HIGH_LEVEL < ph < 14:
            self.reduce_ph()

        return dict(
            ph=ph
        )
