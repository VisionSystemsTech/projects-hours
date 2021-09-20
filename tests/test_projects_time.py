# todo: mocked bot tests
import pytest
import json
from datetime import date
import pandas as pd

from src.database import DataBase


class TestDataBase:
    @staticmethod
    def set_up(tmp_path):
        def make_date(i=0):
            return str(date(2020, 9, 7 + i))

        data = [
            {'project': 'project1', 'employee': 'e1', 'date': make_date(), 'week': make_date(), 'hours': 8},
            {'project': 'project2', 'employee': 'e1', 'date': make_date(1), 'week': make_date(), 'hours': 2},
            {'project': 'project1', 'employee': 'e2', 'date': make_date(), 'week': make_date(), 'hours': 8},
            {'project': 'project1', 'employee': 'e2', 'date': make_date(1), 'week': make_date(), 'hours': 8},
            {'project': 'project2', 'employee': 'e1', 'date': make_date(1), 'week': make_date(), 'hours': 6},
        ]
        db_url = tmp_path.joinpath('db.json')
        with open(db_url, 'w') as f:
            json.dump(data, f)
        db = DataBase(db_url)
        return db, data

    def test_add_hours(self, tmp_path):
        db, data = self.set_up(tmp_path)
        obtained = db.report_by_employee('e1', 'e2', date(2020, 9, 7))
        expected = 0
        assert expected == obtained.shape[0]

        obtained = db.report_by_employee('e2', 'e2', date(2020, 9, 7))
        expected = pd.DataFrame(data[3:4])
        self.assert_dataframes(expected, obtained)

        obtained = db.report_by_employee('Roman Steinberg', 'e2', date(2020, 9, 7))
        expected = pd.DataFrame(data[2:3])
        self.assert_dataframes(expected, obtained)

    def test_report(self, tmp_path):
        db, data = self.set_up(tmp_path)
        obtained = db.report_by_week('Roman Steinberg', date(2020, 9, 8))
        expected = pd.DataFrame(data[:3])
        expected.loc[1, 'hours'] = 8
        expected.loc[2, 'hours'] = 16
        self.assert_dataframes(expected, obtained)

    @staticmethod
    def assert_dataframes(expected, obtained):
        assert expected.shape[0] == obtained.shape[0]
        for index, row in obtained.iterrows():
            project, employee = row.name
            cond = (expected.project == project) & (expected.employee == str(employee))
            assert expected[cond].shape[0] == 1
            assert expected[cond].iloc[0, 4] == row.hours
