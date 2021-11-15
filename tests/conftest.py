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
def fake_db(reread_config, tmp_path):
    db_path = tmp_path.joinpath('db.json')
    copy2('db/db_example.json', str(db_path))
    SingleConfig().db_path = db_path
    db = DataBase()
    return db
