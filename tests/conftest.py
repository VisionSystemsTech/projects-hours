# -*- coding: utf-8 -*-
import pytest
import json
from shutil import copy2
from datetime import date

from src.utils.config import SingleConfig
from src.database import DataBase


@pytest.fixture(autouse=True)
def reread_config():
    cfg = SingleConfig('config-default.yaml')
    cfg.reset()
    return cfg


@pytest.fixture(autouse=True)
def mock_db(tmp_path):
    db_url = tmp_path.joinpath('db.json')
    copy2('db/db_example.json', str(db_url))
    with open(db_url) as f:
        data = json.load(f)
    db = DataBase(db_url)
    return db, data
