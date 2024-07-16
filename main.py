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
        log("* * *  forceably shut down - tower equipment in unknown state * * *")
        sys.exit(100)


signal.signal(signal.SIGINT, signal_handler)


def daytime_schedule(letusgrow_tower: equipment.LetUsGrowTower):
    log("Event=StartingSchedule, "
        "Schedule=Daytime")
    schedule.clear()
    letusgrow_tower.evaluate_chemistry()
    schedule.every(10).minutes.do(lambda tower: tower.lights.on(), letusgrow_tower)
    schedule.every(1).hours.do(lambda tower: tower.evaluate_chemistry(), letusgrow_tower)
    schedule.every(15).minutes.do(lambda tower: tower.watering_pump.toggle(), letusgrow_tower)
    schedule.every(10).minutes.do(lambda tower: tower.state_audit(), letusgrow_tower)


def nighttime_schedule(letusgrow_tower: equipment.LetUsGrowTower):
    log("Event=StartingSchedule, "
        "Schedule=Nighttime")
    schedule.clear()
    # letusgrow_tower.lights.off()
    schedule.every(10).minutes.do(lambda tower: tower.lights.off(), letusgrow_tower)
    schedule.every().hour.at(":00").do(lambda tower: tower.watering_pump.on(), letusgrow_tower)
    schedule.every().hour.at(":15").do(lambda tower: tower.watering_pump.off(), letusgrow_tower)
    schedule.every(10).minutes.do(lambda tower: tower.state_audit(), letusgrow_tower)


if __name__ == '__main__':
    relay_board = equipment.USBRelayBoard8(configuration.RELAY_BOARD_ID)
    letusgrow = equipment.LetUsGrowTower(relay_board)

    # default to initially running the daytime schedule once
    daytime_schedule(letusgrow)

    schedule.every().day.at(configuration.DAYTIME_SCHEDULE_START_TIME).do(daytime_schedule, letusgrow)
    schedule.every().day.at(configuration.NIGHTTIME_SCHEDULE_START_TIME).do(nighttime_schedule, letusgrow)
    
    while True:
        schedule.run_pending()
        time.sleep(1)
