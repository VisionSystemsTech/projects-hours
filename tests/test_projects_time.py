# -*- coding: utf-8 -*-
# todo: mocked bot tests
import pytest

from datetime import date
import pandas as pd


def test_add_hours(tmp_path, mock_db):
    db = mock_db
    obtained = db.report_by_employee('sean', 'serg', date(2021, 2, 1))
    expected = 0
    assert expected == obtained.shape[0]

    obtained = db.report_by_employee('sean', 'sean', date(2021, 2, 1))
    expected = pd.DataFrame([{'project': 'Detector', 'employee': 'sean', 'hours': 16}])
    assert_dataframes(expected, obtained)

    obtained = db.report_by_employee('serg', 'sean', date(2021, 2, 1))
    assert_dataframes(expected, obtained)


def test_report(tmp_path, mock_db):
    db = mock_db
    obtained = db.report_by_week('serg', date(2021, 2, 1))
    expected = pd.DataFrame([
        {'project': 'Classifier', 'employee': 'serg', 'hours': 8},
        {'project': 'Detector', 'employee': 'sean', 'hours': 16},
        {'project': 'Detector', 'employee': 'serg', 'hours': 8},
    ])
    assert_dataframes(expected, obtained)


def assert_dataframes(expected, obtained):
    assert expected.shape[0] == obtained.shape[0], 'shapes not equal'
    for index, row in obtained.iterrows():
        # project, employee = row.name
        cond = (expected.project == row.project) & (expected.employee == row.employee)
        assert expected[cond].shape[0] == 1, f'expected not a single row for ({row.project}, {row.employee})'
        err_msg = f'expected another hours for ({row.project}, {row.employee})'
        assert expected[cond].iloc[0]['hours'] == row.hours, err_msg
