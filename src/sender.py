# -*- coding: utf-8 -*-
import logging
from datetime import date

from requests import post


class Sender:
    def __init__(self, token):
        self._token = token

    def run(self, message_guid, author, message):
        logger = logging.getLogger(__name__)
        logger.info(f'guid: {message_guid}, author: {author},  received message: {message}')

        fields = message.split(',')
        fields = list(map(lambda s: s.strip(), fields))
        if len(fields) not in [2, 3]:
            logger.error(f'guid: {message_guid}, error message: incorrect format')
            return False

        project, time, date_, *_ = fields + [str(date.today())]
        url = 'https://script.google.com/macros/s/AKfycbwpYMvLkyDWwhnITBISl-yif80KubJf6fkxiJYW_U1Pr5kLrQE/exec'
        record = {'author': author, 'project': project, 'time': time, 'date': date_}
        logger.info(f'guid: {message_guid}, sending record: {record}')
        response = post(url, json={'record': record})
        logger.info(response.text)
        return True if response.status_code == 200 else False
