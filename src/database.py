# -*- coding: utf-8 -*-
import json
from datetime import date, timedelta, datetime
from pathlib import Path
from typing import List, Dict

import numpy as np
import pandas as pd

from src.utils.config import SingleConfig


class DataBase:
    _db_url: Path
    _history: pd.DataFrame
    _employees: List[Dict]
    _projects: List[Dict]

    def __init__(self):
        self._db_url = SingleConfig().db_url
        with open(self._db_url) as f:
            data = json.load(f)
        self._employees = data['employees']
        self._projects = data['projects']
        self._history = pd.DataFrame(data['history'])  # pd.read_json(self._db_url, orient='records')

    # -----------------------
    # Utility methods
    # -----------------------

    def dump(self):
        h = self._history.to_json()
        d = {
            'employees': self._employees,
            'projects': self._projects,
            'history': self._history.to_json()
        }
        with self._db_url.open('w') as f:
            json.dump(d, f)


    @staticmethod
    def get_week(day: date) -> tuple:
        start = day - timedelta(days=day.weekday())
        end = start + timedelta(days=6)
        return start, end

    @staticmethod
    def get_week_start(day: date) -> date:
        return day - timedelta(days=day.weekday())

    def is_valid_employee(self, tg_nick: str):
        return any([tg_nick == rec['tg_nick'] for rec in self._employees])

    def is_manager(self, tg_nick: str):
        return any([tg_nick == rec['tg_nick'] for rec in self._employees if rec['role'] == 'manager'])

    def is_valid_project(self, project_name: str):
        return any([project_name == rec['name'] for rec in self._projects])

    # -----------------------
    # Action methods
    # -----------------------

    def add_hours(self, telegram_user_name: str, project: str, day: date, hours: int):
        # Add hours
        week_start = str(DataBase.get_week_start(day))
        self._history.append({
            'project': project, 'employee': telegram_user_name, 'date': day, 'week': week_start, 'hours': hours
        })
        self._history.sort_values(by=['employee', 'project'])
        self.dump()
        return True, ''

    def report_by_week(self, user: str, day: date):
        # Prepare view
        cond = self._history.week == str(DataBase.get_week_start(day))
        view = self._history[cond]

        # Rights check
        if not self.is_manager(user):
            view = view[view.employee == user]

        # Process view before return
        view = view.groupby(by=['project', 'employee'], as_index=False)
        return view.aggregate(np.sum)

    def report_by_employee(self, user: str, employee: str, day: date):
        # Prepare view
        cond = self._history.week == str(DataBase.get_week_start(day))
        view = self._history[cond]

        # Rights check
        if user == employee or self.is_manager(user):
            view = view[view.employee == employee]
        else:
            return view.drop(view.index)

        # Process view before return
        view = view.groupby(by=['project', 'employee'], as_index=False)
        return view.aggregate(np.sum)
