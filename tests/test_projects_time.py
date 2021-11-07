# -*- coding: utf-8 -*-
# todo: mocked bot tests
import pytest

from datetime import date
import pandas as pd


def test_add_hours(tmp_path, mock_db):
    db, data = mock_db
    obtained = db.report_by_employee('e1', 'e2', date(2020, 9, 7))
    expected = 0
    assert expected == obtained.shape[0]

    obtained = db.report_by_employee('e2', 'e2', date(2020, 9, 7))
    expected = pd.DataFrame(data[3:4])
    assert_dataframes(expected, obtained)

    obtained = db.report_by_employee('Roman Steinberg', 'e2', date(2020, 9, 7))
    expected = pd.DataFrame(data[2:3])
    assert_dataframes(expected, obtained)


def test_report(tmp_path, mock_db):
    db, data = mock_db
    obtained = db.report_by_week('Roman Steinberg', date(2020, 9, 8))
    expected = pd.DataFrame(data[:3])
    expected.loc[1, 'hours'] = 8
    expected.loc[2, 'hours'] = 16
    assert_dataframes(expected, obtained)


def assert_dataframes(expected, obtained):
    assert expected.shape[0] == obtained.shape[0]
    for index, row in obtained.iterrows():
        project, employee = row.name
        cond = (expected.project == project) & (expected.employee == str(employee))
        assert expected[cond].shape[0] == 1
        assert expected[cond].iloc[0, 4] == row.hours
