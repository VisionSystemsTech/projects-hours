# -*- coding: utf-8 -*-
from datetime import date, timedelta, datetime
from typing import List

import pandas as pd
import numpy as np


class DataBase:
    _db_url: str
    _data: pd.DataFrame
    _managers: List = ['Roman Steinberg', 'Artem Kondrashkin']

    def __init__(self, db_url):
        self._db_url = db_url
        self._data = pd.read_json(db_url, orient='records')

    def dump(self):
        self._data.to_json(self._db_url)

    def add_hours(self, telegram_user_name: str, project: str, day: date, hours: int):
        employee = self._employees.get(telegram_user_name)
        if employee is None:
            return False, 'Incorrect user.'

        if project not in self._projects:
            return False, 'Incorrect project name.'

        if not isinstance(hours, int):
            return False, 'Hours should be int.'

        if not isinstance(day, date):
            return False, 'Incorrect date.'

        week_start = str(day - timedelta(days=day.weekday()))
        self._data.append({'project': project, 'employee': employee, 'date': day, 'week': week_start, 'hours': hours})
        self._data.sort_values(by=['employee', 'project'])
        self.dump()
        return True, ''

    def report_by_week(self, user: str, day: date):
        week_start = day - timedelta(days=day.weekday())
        cond = self._data.week == str(week_start)
        view = self._data[cond]
        if not self.show_all(user):  # filter by user
            view = view[view.employee == user]
        view = view.groupby(by=['project', 'employee'])  # count
        return view.aggregate(np.sum)

    def report_by_employee(self, user: str, employee: str, day: date):
        cond = self._data.date == datetime.combine(day, datetime.min.time())
        view = self._data[cond]
        if user == employee or self.show_all(user):  # filter by employee
            view = view[view.employee == employee]
        else:
            return view.drop(view.index)
        view = view.groupby(by=['project', 'employee'])  # count
        return view.aggregate(np.sum)

    def show_all(self, user: str):
        return user in self._managers

    @property
    def _employees(self):
        return self._data.empoyee.unique()

    @property
    def _projects(self):
        return self._data.project.unique()

    @staticmethod
    def week(day: date) -> tuple:
        start = day - timedelta(days=day.weekday())
        end = start + timedelta(days=6)
        return start, end
