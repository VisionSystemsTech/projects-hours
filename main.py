# -*- coding: utf-8 -*-
from pathlib import Path

import yaml

from src.controller import TimeCounterBot


if __name__ == '__main__':
    path = Path('config.yaml')
    if not path.exists():
        print('Скопируйте файл default-config.yaml, переименуйте его в config.yaml, укажите параматеры.')
        exit()
    with path.open() as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    # import pandas as pd
    # df = pd.DataFrame(columns=['project', 'employee', 'date', 'hours'])
    # df.to_json('db/data.json')
    bot = TimeCounterBot(config)
    bot.start()
