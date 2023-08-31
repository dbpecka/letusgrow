import schedule
from datetime import datetime, timedelta, time
import equipment
import configuration


def daytime_schedule(letusgrow_tower: equipment.LetUsGrowTower):
    schedule.clear()
    letusgrow_tower.lights.on()
    schedule.every(15).minutes().do(lambda tower: tower.watering_pump.toggle(), letusgrow_tower)
    print("Starting daytime schedule")


def nighttime_schedule(letusgrow_tower: equipment.LetUsGrowTower):
    schedule.clear()
    letusgrow_tower.lights.off()
    schedule.every().hour.at(":00").do(lambda tower: tower.watering_pump.on(), letusgrow_tower)
    schedule.every().hour.at(":15").do(lambda tower: tower.watering_pump.off(), letusgrow_tower)
    print("Starting nighttime schedule")


if __name__ == '__main__':
    relay_board = equipment.USBRelayBoard8(configuration.RELAY_BOARD_COM_STRING, configuration.RELAY_BOARD_BAUD)
    letusgrow = equipment.LetUsGrowTower(relay_board)

    print(1)
    schedule.every().day.at(configuration.DAYTIME_SCHEDULE_START_TIME).do(daytime_schedule, letusgrow)
    print(2)
    schedule.every().day.at(configuration.NIGHTTIME_SCHEDULE_START_TIME).do(nighttime_schedule, letusgrow)
    print(3)

