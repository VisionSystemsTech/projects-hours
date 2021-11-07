# -*- coding: utf-8 -*-
import logging
from uuid import uuid4
from datetime import date

from telegram import Update
from telegram.ext import Filters, MessageHandler, CommandHandler, CallbackContext, ConversationHandler
from telegram.ext import Updater

from src.sender import Sender
from src.database import DataBase


class TimeCounterBot:
    """
    Класс выполняет роль контроллера. Предназначен для настройки и запуска бота.
    """
    def __init__(self, config):
        self.updater = Updater(token=config.token, use_context=True)  # заводим апдейтера
        self._init_conversation()

        fmt_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        level = logging._nameToLevel(config.general.logging_level)
        logging.basicConfig(filename='bot.log', format=fmt_str, level=level)
        self._logger = logging.getLogger(__name__)

        self._sender = Sender(config.token)
        self._db = DataBase()

    def _init_conversation(self):
        handler = CommandHandler('help', self.help)
        self.updater.dispatcher.add_handler(handler)

        handler = CommandHandler('update', self.update_table)
        self.updater.dispatcher.add_handler(handler)

        handler = CommandHandler('report', self.report)
        self.updater.dispatcher.add_handler(handler)

        entry_points = [CommandHandler(['add_hours'], self.before_add_hours)]
        states = {
            'adding_hours': [MessageHandler(Filters.text, self.add_hours)],
        }
        fallbacks = []
        handler = ConversationHandler(entry_points, states, fallbacks)
        self.updater.dispatcher.add_handler(handler)

    def start(self):
        self.updater.start_polling()
        self.updater.idle()

    def add_hours(self, update: Update, context: CallbackContext):
        self._logger.debug(f'User {update.message.from_user.username} requested to add hours.')
        guid = uuid4()
        chat_id = update.message.chat_id
        # logger = logging.getLogger(__name__)
        # logger.info('rrr')
        tg_user_name = update.message.from_user.username
        success, input_data = self.parse_hours_message(tg_user_name, update.message.text)
        if not success:
            context.bot.send_message(chat_id=chat_id, text='Incorrect input data format')
            return
        success, error_message = self._db.add_hours(tg_user_name, **input_data)
        # result = self._sender.run(guid, name, update.message.text)
        text = 'Successfully recorded.' if success else f'Failed. {error_message}'
        context.bot.send_message(chat_id=chat_id, text=text)

    def parse_hours_message(self, telegram_user_name, message):
        fields = message.split(',')
        fields = list(map(lambda s: s.strip(), fields))
        if len(fields) not in [2, 3]:
            return False, None

        project, hours, day, *_ = fields + [str(date.today())]

        # Data validation
        if not self._db.is_valid_employee(telegram_user_name):  # todo: сделать для всех запросов
            return False, f'Incorrect user {telegram_user_name}.'

        if not self._db.is_valid_project(project):
            return False, f'Incorrect project name {project}.'

        try:
            hours = int(hours)
        except ValueError:
            return False, 'Hours must be int.'

        try:
            day = date.fromisoformat(day)
        except ValueError:
            return False, f'Incorrect date {day}'

        input_data = {'project': project, 'hours': hours, 'day': day}
        return True, input_data

    @staticmethod
    def help(update: Update, context: CallbackContext):
        context.bot.send_message(chat_id=update.effective_chat.id, text='You can /add_hours, /report [date], ...')

    @staticmethod
    def before_add_hours(update: Update, context: CallbackContext):
        context.bot.send_message(chat_id=update.effective_chat.id, text='Send time in format \"project,time[,day]\"')
        return 'adding_hours'

    def report(self, update: Update, context: CallbackContext):
        self._logger.debug(f'User {update.message.from_user.username} requested for the report.')
        if len(context.args) > 0:
            day, month, year = context.args[0].split('.')
            day = date(year, month, day)
        else:
            day = date.today()
        tg_user_name = update.message.from_user.username
        text = self._db.report_by_week(tg_user_name, day).to_string()
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    def update_table(self, update: Update, context: CallbackContext):
        # self._sender.run
        pass
