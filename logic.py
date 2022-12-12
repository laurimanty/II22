'''
Module to help with formatting database information for the frontend
'''

from tabulate import tabulate
from database_helper import DB_helper
import datetime

def get_all_event_data(db_object: DB_helper):
    data = db_object.get_all_events()
    table_data = []
    for i in data:
        table_data.append(list(i.values()))

    headers = ["Event ID", "Robot ID", "Event type", "Time", "Alarm activated"]
    table = tabulate(table_data, headers, tablefmt="html", numalign="left")
    
    return table

def get_robot_states(db_object: DB_helper):
    data = db_object.get_latest_events()
    state_data = []
    for robot in data:
        state_data.append(list(robot.values())[1:])

    headers = ["Robot ID", "Event type", "Time", "Alarm activated"]
    table = tabulate(state_data, headers, tablefmt="html", numalign="left")
    return table


def get_alarms_history(db_object: DB_helper):
    data = db_object.get_latest_events()
    for robot in data:
        robot = (list(robot.values()))
        if (not robot[4]) and (robot[2] in ['DOWN', 'READY-IDLE-BLOCKED', 'READY-IDLE-STARVED', 'IDLE']) \
                             and (datetime.datetime.now() - datetime.datetime.strptime(robot[3], '%Y-%m-%d %H:%M:%S.%f') > datetime.timedelta(minutes=1)) :
                db_object.update_flagged(robot[0])
                if robot[2] in ['READY-IDLE-BLOCKED', 'READY-IDLE-STARVED', 'IDLE']: alarm_text = "TOO LONG IN IDLE STATE"
                elif robot[2] == 'DOWN': alarm_text = "TOO LONG IN DOWN STATE" 
                else: alarm_text = "UNKOWN ERROR"
                db_object.insert_flaggedevent(robotID=robot[1], eventype=alarm_text)

    alarms_data = db_object.get_all_alarmevents()
    state_data = []
    for alarm in alarms_data:
        state_data.append(list(alarm.values()))

    headers = ["List index", "Robot ID", "Alarm type", "Time"]
    table = tabulate(state_data, headers, tablefmt="html", numalign="left")
    return table