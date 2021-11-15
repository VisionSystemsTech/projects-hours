# -*- coding: utf-8 -*-
import yaml
from copy import deepcopy
from pathlib import Path

from easydict import EasyDict


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class SingleConfig(metaclass=SingletonMeta):
    def __init__(self, user_source='config.yaml', default_source='config-default.yaml'):
        self._keys = list()
        self._user_source = user_source
        self._default_source = default_source
        self.reset()

    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        else:
            raise AttributeError(name)

    def __getitem__(self, name):
        return getattr(self, name)

    def get_part(self, subconfig):
        partial_config = {} if self[subconfig] is None else deepcopy(self[subconfig])
        partial_config.update(self['general'])
        return partial_config

    def reset(self):
        for key in self._keys:
            delattr(self, key)
        self._keys = list()

        d = EasyDict(self._load_config())
        for k, v in d.items():
            setattr(self, k, v)
            self._keys.append(k)

    def _load_config(self):
        config = self._read_config(self._default_source)
        user_config = dict()
        if Path(self._user_source).exists():
            user_config = self._read_config(self._user_source)

        config_issues = list()
        is_valid = self._update_config(config, user_config, str_to_print=self._default_source, to_print=config_issues)
        if config_issues:
            print(f'Problem(s) with configs:\n{"".join(config_issues)}\n'
                  f'Check and correct your {self._make_bold(self._default_source)} '
                  f'and {self._make_bold(self._user_source)}!')
        if not is_valid:
            exit(0)

        working_dir = Path(config['general']['working_dir']).absolute()
        resources_dir = Path(config['general']['resources_dir']).absolute()
        config['general']['working_dir'] = str(working_dir)
        self._set_absolute_paths(config, working_dir, resources_dir)

        return config

    @staticmethod
    def _read_config(source):
        if isinstance(source, str):
            with open(source, 'r') as stream:
                config = yaml.safe_load(stream)
            if config is None:
                print(f'{source} is empty. Fill it, please.')
                exit()
        else:
            raise TypeError('Unexpected source to load config')
        return config

    @staticmethod
    def _update_config(default_cfg, user_cfg, str_to_print, to_print):
        result = True
        if type(default_cfg) != type(user_cfg):
            to_print.append(f'{str_to_print} have different types: {type(default_cfg)} and {type(user_cfg)}\n')
            result = False
        elif isinstance(user_cfg, dict):
            for key, value in user_cfg.items():
                if key not in default_cfg:
                    to_print.append(f'No key in {str_to_print} '
                                    f'{SingleConfig._get_delimiter_key()} '
                                    f'{SingleConfig._make_bold(key)}\n')
                    result = False
                elif isinstance(value, dict):
                    new_str = f'{str_to_print} {SingleConfig._get_delimiter_key()} {key}'
                    cfg1, cfg2 = default_cfg[key], value
                    result = SingleConfig._update_config(cfg1, cfg2, new_str, to_print) and result
                else:
                    default_cfg[key] = value

        return result

    @staticmethod
    def _set_absolute_paths(d, working_dir, resources_dir):
        for key, value in d.items():
            if isinstance(d[key], dict):
                if key.strip() == 'resources':
                    for sub_key, sub_value in value.items():
                        value[sub_key] = str(resources_dir.joinpath(sub_value))
                else:
                    SingleConfig._set_absolute_paths(d[key], working_dir, resources_dir)
            else:
                if value is not None:
                    if 'path' in key:
                        d[key] = working_dir.joinpath(value)
                    elif 'location' in key:
                        d[key] = resources_dir.joinpath(value)

    @staticmethod
    def _make_bold(s):
        bold = '\033[1m'
        end_bold = '\033[0m'
        return bold + s + end_bold

    @staticmethod
    def _get_delimiter_key():
        return '->'
