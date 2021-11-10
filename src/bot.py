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
            entry_points=[CommandHandler('start', self.say_welcome)],
            # entry_points=[CallbackQueryHandler(self.say_welcome, pattern='start')],
            states={
                States.MENU: [
                    CommandHandler('add_hours', self.before_add_hours),
                    CommandHandler('report', self.report),
                    CommandHandler('projects', self.show_projects),
                    # CallbackQueryHandler(self.before_add_hours, pattern='add_hours'),
                    # CallbackQueryHandler(self.report, pattern='report'),
                    # CallbackQueryHandler(self.show_projects, pattern='projects'),
                    # CallbackQueryHandler(self.project_button, pattern='projects'),
                ],
                States.ADD_HOURS: [MessageHandler(Filters.text, self.add_hours)],
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
            # per_message=True,
        )
        self._updater.dispatcher.add_handler(handler)

    def start(self):
        self._updater.start_polling()
        self._updater.idle()

    def say_welcome(self, update: Update, context: CallbackContext):
        """Начинает диалог и предлагает меню"""
        reply_keyboard = [[
            InlineKeyboardButton('Проекты', callback_data='/projects'),
            InlineKeyboardButton('Отчет', callback_data='/report'),
            InlineKeyboardButton('Часы', callback_data='/add_hours'),
        ]]

        update.message.reply_text(
            'Привет!',
            reply_markup=InlineKeyboardMarkup(
                reply_keyboard, one_time_keyboard=False
            ),
        )
        return States.MENU

    def add_hours(self, update: Update, context: CallbackContext):
        self._logger.debug(f'User {update.message.from_user.username} requested to add hours.')
        chat_id = update.message.chat_id
        tg_user_name = update.message.from_user.username
        success, error_message = self._controller.add_hours(tg_user_name, update.message.text)
        if not success:
            context.bot.send_message(chat_id=chat_id, text=error_message)
            return
        # update.message.reply_text(
        context.bot.send_message(chat_id=chat_id, text='Successfully recorded.')
        return States.MENU

    @staticmethod
    def help(update: Update, context: CallbackContext):
        context.bot.send_message(chat_id=update.effective_chat.id, text='You can /add_hours, /report [date], ...')

    @staticmethod
    def before_add_hours(update: Update, context: CallbackContext):
        context.bot.send_message(chat_id=update.effective_chat.id, text='Send time in format \"project,time[,day]\"')
        return States.ADD_HOURS

    def report(self, update: Update, context: CallbackContext):
        self._logger.debug(f'User {update.message.from_user.username} requested for the report.')
        tg_user_name = update.message.from_user.username
        message = update.message.text
        text = self._controller.report(tg_user_name, message)
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    def show_projects(self, update: Update, context: CallbackContext):
        self._logger.debug(f'User {update.message.from_user.username} requested the list of projects.')
        text = self._controller.show_projects(update.message.text)
        context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    def cancel(self, update: Update, context: CallbackContext) -> int:
        """Cancels and ends the conversation."""
        user = update.message.from_user
        self._logger.debug(f'User {user.username} canceled the conversation.')
        update.message.reply_text(
            'Bye! I hope we can talk again some day.' # , reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END