# -*- coding: utf-8 -*-
import logging
from uuid import uuid4

from enum import Enum
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Filters, MessageHandler, CommandHandler, CallbackContext, ConversationHandler, \
    CallbackQueryHandler
from telegram.ext import Updater

from src.controller import Controller
from src.utils.config import SingleConfig


class States(Enum):
    MENU = 0
    ADD_HOURS = 1
    DELETE_HOURS = 2


class HoursCounterBot:
    """
        Класс предназначен для настройки и запуска бота.
    """

    def __init__(self):
        config = SingleConfig()
        self._updater = Updater(token=config.token, use_context=True)  # заводим апдейтера
        self._init_conversation()

        fmt_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        level = logging._nameToLevel[config.general.logging_level]
        logging.basicConfig(filename='bot.log', format=fmt_str, level=level)
        self._logger = logging.getLogger(__name__)

        self._controller = Controller()

    def _init_conversation(self):
        # todo: error handler
        handler = ConversationHandler(
            entry_points=[
                CommandHandler('start', HoursCounterBot.say_welcome),
            ],
            states={
                States.MENU: [
                    CommandHandler('add_hours', HoursCounterBot.before_add_hours),
                    CommandHandler('delete_hours', HoursCounterBot.before_delete_hours),
                    CommandHandler('report', self.report),
                    CommandHandler('projects', self.show_projects),
                ],
                States.ADD_HOURS: [MessageHandler(Filters.text, self.add_hours)],
                States.DELETE_HOURS: [MessageHandler(Filters.text, self.delete_hours)],
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
        )
        self._updater.dispatcher.add_handler(handler)

    def start(self):
        self._updater.start_polling()
        self._updater.idle()

    @staticmethod
    def say_welcome(update: Update, context: CallbackContext):
        """Начинает диалог и предлагает меню"""
        HoursCounterBot.help(update, context)
        return States.MENU

    @staticmethod
    def help(update: Update, context: CallbackContext):
        """Подсказка"""
        update.message.reply_text('Привет! Вы можете использовать следующие команды:\n'
                                  '/projects - список активных проектов,\n'
                                  '/add_hours - добавление часов к рабочей неделе (неделя определяется '
                                  'указанием даты, любой входящей в нужную неделю),\n'
                                  '/delete_hours - удаление часов за рабочую неделю (неделя определяется '
                                  'указанием даты, любой входящей в нужную неделю),\n'
                                  '/report [date] - отчет по часам (если дата не указана, то по '
                                  'умолчанию используется сегодняшняя.\n'
                                  'Формат дат ISO: ГГГГ-ММ-ДД.')

    @staticmethod
    def before_add_hours(update: Update, context: CallbackContext):
        update.message.reply_text('Формат \"проект,часы[,дата]\".')
        return States.ADD_HOURS

    def before_delete_hours(update: Update, context: CallbackContext):
        update.message.reply_text('Укажите дату, относящуюся к неделе, в которой надо удалить часы.')
        return States.DELETE_HOURS

    def add_hours(self, update: Update, context: CallbackContext):
        self._logger.info(f'User {update.message.from_user.username} requested to add hours.')
        tg_user_name = update.message.from_user.username
        success, error_message = self._controller.add_hours(tg_user_name, update.message.text)
        if not success:
            update.message.reply_text(error_message)
            return
        update.message.reply_text('Часы добавлены.')
        return States.MENU

    def delete_hours(self, update: Update, context: CallbackContext):
        self._logger.info(f'User {update.message.from_user.username} requested to delete hours.')
        tg_user_name = update.message.from_user.username
        success, n, error_message = self._controller.delete_hours(tg_user_name, update.message.text)
        if not success:
            update.message.reply_text(error_message)
            return
        reply_message = 'Часы удалены.' if n > 0 else f'На неделе с датой {update.message.text} часов не было введено.'
        update.message.reply_text(reply_message)
        return States.MENU

    def report(self, update: Update, context: CallbackContext):
        self._logger.info(f'User {update.message.from_user.username} requested for the report.')
        tg_user_name = update.message.from_user.username
        message = update.message.text
        if '/report' in message:
            message = message[7:]
        text = self._controller.report(tg_user_name, message)
        update.message.reply_text(text)

    def show_projects(self, update: Update, context: CallbackContext):
        self._logger.info(f'User {update.message.from_user.username} requested the list of projects.')
        message = update.message.text
        if '/projects' in message:
            message = message[9:]
        text = self._controller.show_projects(message)
        update.message.reply_text(text)

    def cancel(self, update: Update, context: CallbackContext) -> int:
        """Cancels and ends the conversation."""
        user = update.message.from_user
        self._logger.info(f'User {user.username} canceled the conversation.')
        update.message.reply_text(
            'Завершаю разговор.'  # , reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
