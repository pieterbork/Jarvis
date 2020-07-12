from datetime import datetime, timedelta
import requests
import marshal
import logging
import base64
import time
import json
import re

from . import Contact, Schedule, Action
from .base_module import BaseModule
from ..settings import SCRIPTS
from .. import utils

class SchedulingModule(BaseModule):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.sms_consumer = True
        self.logger.debug('debug test')

    def get_day(self, day):
        daystr = day.lower()
        if daystr == 'monday':
            return 0
        elif daystr == 'tuesday':
            return 1
        elif daystr == 'wednesday':
            return 2
        elif daystr == 'thursday':
            return 3
        elif daystr == 'friday':
            return 4
        elif daystr == 'saturday':
            return 5
        elif daystr == 'sunday':
            return 6

    def parse_interval(self, parts):
        self.logger.info("Trying to parse {} into a start date and interval")
        run_date = None
        interval = None
        num = len(parts)
        if num > 1 and parts[0] == 'every':
            if parts[1] == 'week':
                interval = 'weekly'
            elif parts[1] == 'month':
                interval = 'monthly'
            elif parts[1] == 'day':
                interval = 'daily'
            elif parts[1] == 'minute':
                interval = 'minutely'
        now = datetime.now()
        if 'on' in parts and num > 2:
            day_num = self.get_day(parts[3])
            run_date = now.replace(hour=12, minute=0, second=0)
            while run_date.weekday() != day_num:
                run_date += timedelta(days=1)
        if not run_date:
            run_date = now

        return (run_date, interval)

    def get_next_run(self, run_date, interval):
        if interval == 'monthly':
            #Get first day next month...
            pass
        elif interval == 'weekly':
            return run_date + timedelta(days=7)
        elif interval == 'daily':
            return run_date + timedelta(days=1)
        elif interval == 'hourly':
            return run_date + timedelta(hours=1)
        elif interval == 'minutely':
            return run_date + timedelta(minutes=1)

    def schedule_script(self, contact, parts):
        resp = None
        for KEY,VALS in SCRIPTS.items():
            self.logger.info("{}:{}".format(KEY, VALS))
            if parts[0] == KEY or parts[0] in VALS['aliases']:
                script = KEY
                args = VALS['args']
                if len(parts) > 2:
                    run_date, interval = self.parse_interval(parts[1:])
                    if not run_date or not interval:
                        self.logger.info("Couldn't parse interval or start date.")
                    else:
                        self.logger.info("Selected run date of {} with interval {}".format(run_date, interval))
                        self.logger.info("Creating schedule for script {} args {}".format(script, args))
                        sched = Schedule(script, 'script', run_date, interval=interval, arguments=args)
                        user = utils.get_user_from_contact(self.session, contact)
                        user.schedules.append(sched)
                        self.session.add(user)
                        self.session.commit()
                        resp = "Scheduled script {} with next_run of {} and interval {}".format(script, run_date, interval)
        return resp

    def get_ready_schedules(self):
        now = datetime.now()
        ready_schedules = self.session.query(Schedule).filter(Schedule.next_run <= now).all()
        return ready_schedules

    def get_overdue_schedules(self):
        overdue_schedules = self.session.query(Schedule).filter(Schedule.last_action == 'due').all()
        return overdue_schedules

    def run_schedules(self, schedules):
        for schedule in schedules:
            self.logger.info("Running schedule: {}".format(schedule))
            if schedule.type == 'script':
                resp = utils.run_script(schedule.name, marshal.loads(schedule.arguments))
                contact = utils.get_user_contact(self.session, schedule.user_id)
                contact.send_sms(resp)
                schedule.add_action(Action('completed'))
                if not schedule.interval:
                    self.session.add(schedule)
                    self.session.commit()
            #Time to schedule next run!
            if schedule.interval:
                next_run = self.get_next_run(schedule.next_run, schedule.interval)
                schedule.set_next_run(next_run)
                self.session.add(schedule)
                self.session.commit()

    def get_message_response(self, contact, msg):
        resp = None
        parts = msg.split()
        if parts[0] == 'schedule':
            if len(parts) > 1 and parts[1] == 'script':
                if len(parts) > 2:
                    resp = self.schedule_script(contact, parts[2:])
        return resp

    def process_message(self, contact, msg):
        body = msg.body
        resp = self.get_message_response(contact, body.lower())
        if resp:
            contact.send_sms(resp)
        else:
            self.logger.info("Couldn't figure out a response...")

    def run_scheduled_tasks(self):
        ready = self.get_ready_schedules()
        self.logger.info("There are {} schedules ready to run!".format(len(ready)))
        self.run_schedules(ready)
        overdue = self.get_overdue_schedules()
        self.logger.info("There are {} overdue schedules".format(len(overdue)))

