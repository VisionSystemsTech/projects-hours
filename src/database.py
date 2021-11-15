# -*- coding: utf-8 -*-
import json
from datetime import date, timedelta, datetime
from pathlib import Path
from typing import List, Dict, Tuple

import numpy as np
import pandas as pd

from src.utils.config import SingleConfig


class DataBase:
    _db_path: Path
    _history: pd.DataFrame
    _employees: List[Dict]
    _projects: List[Dict]

    def __init__(self):
        self._db_path = SingleConfig().db_path
        with open(self._db_path) as f:
            data = json.load(f)
        self._employees = data['employees']
        self._projects = data['projects']
        self._history = pd.DataFrame.from_records(data['history'])

    # -----------------------
    # Utility methods
    # -----------------------

    def dump(self):
        d = {
            'employees': self._employees,
            'projects': self._projects,
            'history': self._history.to_dict('records')
        }
        with self._db_path.open('w') as f:
            json.dump(d, f, ensure_ascii=False)

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

    def add_hours(self, telegram_user_name: str, project: str, day: date, hours: int) -> Tuple[bool, str]:
        # Add hours
        week_start = DataBase.get_week_start(day)
        self._history = pd.concat(
            [
                self._history,
                pd.DataFrame({
                    'project': [project],
                    'employee': [telegram_user_name],
                    'date': [str(day)],
                    'week': [str(week_start)],
                    'hours': [hours]
                })
            ],
            ignore_index=True
        )
        self._history.sort_values(by=['employee', 'project'])
        self.dump()
        return True, ''

    def delete_hours(self, tg_user_name: str, day: date):
        week_start = DataBase.get_week_start(day)
        indexes_to_remove = self._history[
            (self._history['week'] == str(week_start)) &
            (self._history['employee'] == tg_user_name)
        ].index
        self._history.drop(index=indexes_to_remove, inplace=True)
        self.dump()
        return len(indexes_to_remove)

    def report_by_week(self, user: str, day: date) -> pd.DataFrame:
        # Prepare view
        cond = self._history.week == str(DataBase.get_week_start(day))
        view = self._history[cond]

        # Rights check
        if not self.is_manager(user):
            view = view[view.employee == user]

        # Process view before return
        view = view.groupby(by=['project', 'employee'], as_index=False)
        return view.aggregate(np.sum)

    def report_by_employee(self, user: str, employee: str, day: date) -> pd.DataFrame:
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

    def get_projects(self, day: date) -> List[str]:
        actual = DataBase.get_week_start(day)
        result = list()
        for project in self._projects:
            if date.fromisoformat(project['date_start']) > actual:
                continue

            if len(project['date_end']) != 0 and date.fromisoformat(project['date_end']) < actual:
                continue

            result.append(project['name'])
        return result
