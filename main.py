import sys
import time
import signal
import schedule
import datetime
import json

from util import log
import equipment
import configuration


letusgrow = None

sigint_count = 0


schedule_rotator = schedule.Scheduler()
schedule_runner = schedule.Scheduler()


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


def daytime_schedule(letusgrow_tower: equipment.LetUsGrowTower):
    log("Event=StartingSchedule, "
        "Schedule=Daytime")

    schedule_runner.clear()
    letusgrow_tower.lights.on()

    schedule_runner.every(1).hours.do(lambda tower: tower.evaluate_chemistry(), letusgrow_tower)
    schedule_runner.every(15).minutes.do(lambda tower: tower.watering_pump.toggle(), letusgrow_tower)
    schedule_runner.every(30).minutes.do(lambda tower: tower.state_audit(), letusgrow_tower)


def nighttime_schedule(letusgrow_tower: equipment.LetUsGrowTower):
    log("Event=StartingSchedule, "
        "Schedule=Nighttime")

    schedule_runner.clear()
    letusgrow_tower.lights.off()

    schedule_runner.every(1).hours.do(lambda tower: tower.evaluate_chemistry(), letusgrow_tower)
    schedule_runner.every().hour.at(":00").do(lambda tower: tower.watering_pump.on(), letusgrow_tower)
    schedule_runner.every().hour.at(":15").do(lambda tower: tower.watering_pump.off(), letusgrow_tower)
    schedule_runner.every(30).minutes.do(lambda tower: tower.state_audit(), letusgrow_tower)


if __name__ == '__main__':
    relay_board = equipment.USBRelayBoard8(configuration.RELAY_BOARD_ID)

    if sys.argv[1] == 'controller':
        letusgrow = equipment.LetUsGrowTower(relay_board)
        signal.signal(signal.SIGINT, signal_handler)

        # default to initially running the daytime schedule once
        daytime_start_time = datetime.datetime.strptime(configuration.DAYTIME_SCHEDULE_START_TIME, "%H:%M")
        nighttime_start_time = datetime.datetime.strptime(configuration.NIGHTTIME_SCHEDULE_START_TIME, "%H:%M")
        if daytime_start_time <= datetime.datetime.strptime(datetime.datetime.now().strftime("%H:%M"), "%H:%M") < nighttime_start_time:
            daytime_schedule(letusgrow)
        else:
            nighttime_schedule(letusgrow)

        schedule_rotator.every().day.at(configuration.DAYTIME_SCHEDULE_START_TIME).do(daytime_schedule, letusgrow)
        schedule_rotator.every().day.at(configuration.NIGHTTIME_SCHEDULE_START_TIME).do(nighttime_schedule, letusgrow)

        while True:
            schedule_rotator.run_pending()
            schedule_runner.run_pending()
            time.sleep(5)

    elif sys.argv[1] == 'server':
        letusgrow = equipment.LetUsGrowTower(relay_board, set_relay_states=False)

        from flask import Flask

        app = Flask(__name__)

        @app.route("/chemistry")
        def hello_world():
            return json.dumps(letusgrow.evaluate_chemistry())

        app.run(host=configuration.SERVER_LISTEN.split(':')[0], port=int(configuration.SERVER_LISTEN.split(':')[1]))
