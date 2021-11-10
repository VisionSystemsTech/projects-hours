# -*- coding: utf-8 -*-
import logging
from uuid import uuid4
from datetime import date

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Filters, MessageHandler, CommandHandler, CallbackContext, ConversationHandler, \
    CallbackQueryHandler
from telegram.ext import Updater

from src.sender import Sender
from src.database import DataBase
from src.utils.config import SingleConfig


class Controller:
    """
    Класс выполняет роль контроллера. Предназначен для настройки и запуска бота.
    """
    def __init__(self):
        self._sender = Sender(SingleConfig().token)
        self._db = DataBase()

    def project_button(self, update: Update, context: CallbackContext):
        query = update.callback_query
        variant = query.data
        query.answer() # смотри https://core.telegram.org/bots/api#callbackquery.
        # query.edit_message_text(text=f"Выбранный вариант: {variant}")
        self.show_projects()

    def add_hours(self, tg_user_name: str, input_text: str):
        success, input_data = self._parse_hours_message(tg_user_name, input_text)
        if not success:
            return success, 'Incorrect input data format. Try again.'
        success, error_message = self._db.add_hours(tg_user_name, **input_data)
        # result = self._sender.run(guid, name, update.message.text)
        return success, error_message

    def _parse_hours_message(self, telegram_user_name: str, message: str):
        fields = message.split(',')
        fields = list(map(lambda s: s.strip(), fields))
        if len(fields) not in [2, 3]:
            return False, None

        project, hours, day, *_ = fields + [str(date.today())]

        # Data validation
        try:
            day = date.fromisoformat(day)
        except ValueError:
            return False, f'Incorrect date {day}'

        if not self._db.is_valid_employee(telegram_user_name):  # todo: сделать для всех запросов
            return False, f'Incorrect user {telegram_user_name}.'

        if not self._db.is_valid_project(project):
            return False, f'Incorrect project name {project}.'
        elif project not in self._db.get_projects(day):
            return False, f'The project {project} is not actual now.'

        try:
            hours = int(hours)
        except ValueError:
            return False, 'Hours must be int.'

        input_data = {'project': project, 'hours': hours, 'day': day}
        return True, input_data

    @staticmethod
    def _parse_date(message: str) -> date:
        if len(message) > 0:
            try:
                year, month, day = message.split('-')
                day = date(year, month, day)
            except ValueError:
                day = date.today()
        else:
            day = date.today()
        return day

    def report(self, tg_user_name: str, message: str):
        day = self._parse_date(message)
        reply_text = self._db.report_by_week(tg_user_name, day).to_string(index=False)
        return reply_text

    def show_projects(self, message: str):
        day = self._parse_date(message)
        return ' '.join(self._db.get_projects(day))

    def update_table(self, update: Update, context: CallbackContext):
        # self._sender.run
        pass

