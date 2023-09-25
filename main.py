import sys
import time
import signal
import schedule

from util import log
import equipment
import configuration


letusgrow = None
sigint_count = 0


# if the app is forced to quit, try gracefully shutting down the tower
def signal_handler(sig, frame):
    global letusgrow, sigint_count
    sigint_count += 1
    if sigint_count == 1:
        log("* * *  sigint: attempting graceful tower shutdown  * * *")
        letusgrow.power_down()
    else:
        log("* * *  forceably shut dow - tower equipment in unknown state * * *")
        sys.exit(100)


signal.signal(signal.SIGINT, signal_handler)
signal.pause()


def daytime_schedule(letusgrow_tower: equipment.LetUsGrowTower):
    log("Starting daytime schedule")
    schedule.clear()
    letusgrow_tower.lights.on()
    schedule.every(15).minutes().do(lambda tower: tower.watering_pump.toggle(), letusgrow_tower)
    log("Daytime schedule submitted")


def nighttime_schedule(letusgrow_tower: equipment.LetUsGrowTower):
    log("Starting nighttime schedule")
    schedule.clear()
    letusgrow_tower.lights.off()
    schedule.every().hour.at(":00").do(lambda tower: tower.watering_pump.on(), letusgrow_tower)
    schedule.every().hour.at(":15").do(lambda tower: tower.watering_pump.off(), letusgrow_tower)
    log("Nighttime schedule started")


if __name__ == '__main__':
    relay_board = equipment.USBRelayBoard8(configuration.RELAY_BOARD_ID)
    letusgrow = equipment.LetUsGrowTower(relay_board)

    schedule.every().day.at(configuration.DAYTIME_SCHEDULE_START_TIME).do(daytime_schedule, letusgrow)
    schedule.every().day.at(configuration.NIGHTTIME_SCHEDULE_START_TIME).do(nighttime_schedule, letusgrow)

    while True:
        schedule.run_pending()
        time.sleep(1)
