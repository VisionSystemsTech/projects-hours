# -*- coding: utf-8 -*-
from src.controller import Controller
from src.bot import HoursCounterBot


if __name__ == '__main__':
    # import pandas as pd
    # df = pd.DataFrame(columns=['project', 'employee', 'date', 'hours'])
    # df.to_json('db/data.json')
    HoursCounterBot().start()
