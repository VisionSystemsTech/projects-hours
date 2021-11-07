# -*- coding: utf-8 -*-
from src.controller import TimeCounterBot
from src.utils.config import SingleConfig


if __name__ == '__main__':
    config = SingleConfig()

    # import pandas as pd
    # df = pd.DataFrame(columns=['project', 'employee', 'date', 'hours'])
    # df.to_json('db/data.json')
    bot = TimeCounterBot(config)
    bot.start()
