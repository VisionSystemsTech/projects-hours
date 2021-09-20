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
        token = config['token']
        self.updater = Updater(token=token, use_context=True)  # заводим апдейтера
        self._init_conversation()

        fmt_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(filename='bot.log', format=fmt_str, level=logging.INFO)
        self._logger = logging.getLogger(__name__)

        self._sender = Sender(token)
        self._db = DataBase(config['db_url'])

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
        guid = uuid4()
        chat_id = update.message.chat_id
        # logger = logging.getLogger(__name__)
        # logger.info('rrr')
        user = update.message.from_user
        user_name = f'{user.first_name} {user.last_name}'
        success, input_data = self.parse_hours_message(guid, update.message.text)
        if not success:
            pass
        success, error_message = self._db.add_hours(user_name, **input_data)
        # result = self._sender.run(guid, name, update.message.text)
        text = 'Successfully recorded.' if success else f'Failed. {error_message}'
        context.bot.send_message(chat_id=chat_id, text=text)

    def parse_hours_message(self, message_guid, message):
        fields = message.split(',')
        fields = list(map(lambda s: s.strip(), fields))
        if len(fields) not in [2, 3]:
            self._logger.error(f'guid: {message_guid}, error message: incorrect input data format')
            return False, None

        project, hours, day, *_ = fields + [str(date.today())]
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
        if len(context.args) > 0:
            day, month, year = context.args[0].split('.')
            day = date(year, month, day)
        else:
            day = date.today()
        user = update.message.from_user
        user_name = f'{user.first_name} {user.last_name}'
        text = self._db.report_by_week(user_name, day).to_string()
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    def update_table(self, update: Update, context: CallbackContext):
        # self._sender.run
        pass
