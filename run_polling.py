import logging
import os

import django

from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    KeyboardButton
)
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

os.environ['DJANGO_SETTINGS_MODULE'] = 'beautycity.settings'
django.setup()

from beautycity.settings import TG_TOKEN
from services.models import Salon, Schedule, Service, Specialist


logging.basicConfig(
    filename='app.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

START_CHOICE = 1
LOCATION = 2
NEARBY_SALONS = 3
MASTER = 4
SERVICE = 5
END = ConversationHandler.END


def start(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Выбрать салон', 'Выбрать мастера', 'Выбрать услугу']]

    update.message.reply_text(
        'Привет, давай наведем тебе красоту.\n Можешь выбрать ближайший салон, любимого мастера или услугу.',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True,
            resize_keyboard=True,
        ),
    )

    return START_CHOICE


def nearby_salon(update: Update, context: CallbackContext) -> int:
    user = update.message.location
    salons = Salon.objects.all()
    for salon in salons:
        logger.info(
            "Agreement of %s, %s: %s > Salon location: %s, %s",
            user.longitude,
            user.latitude,
            update.message.location,
            salon.lon,
            salon.lat
        )
    return LOCATION


def master(update: Update, context: CallbackContext) -> int:

    # user = update.message.from_user
    # logger.info("Agreement of %s: %s", user.first_name, update.message.text)
    # update.message.reply_text(
    #     'Пожалуйста, выберете мастера',
    #     reply_markup=ReplyKeyboardRemove(),
    # )

    return MASTER


def service(update: Update, context: CallbackContext) -> int:

    # user = update.message.from_user
    # logger.info("Agreement of %s: %s", user.first_name, update.message.text)
    # update.message.reply_text(
    #     'Пожалуйста, выберите услугу',
    #     reply_markup=ReplyKeyboardRemove(),
    # )

    return SERVICE


def location(update: Update, context: CallbackContext) -> int:
    location_keyboard = KeyboardButton(
        text='Поделиться локацией',
        request_location=True
    )
    custom_keyboard = [[location_keyboard]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
    update.message.reply_text(
        text="Чтобы найти ближайшие салоны, поделитесь своей геолокацией",
        reply_markup=reply_markup
    )
    return LOCATION


def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Очень жаль, что вы не с нами! =(',
        reply_markup=ReplyKeyboardRemove()
    )

    return END


def run_polling():
    updater = Updater(token=TG_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            START_CHOICE: [
                MessageHandler(
                    Filters.regex('^Выбрать салон$'),
                    location
                ),
                MessageHandler(
                    Filters.regex('^Выбрать мастера$'),
                    master
                ),
                MessageHandler(
                    Filters.regex('^Выбрать услугу$'),
                    service
                )
            ],
            LOCATION: [MessageHandler(
                    Filters.location,
                    nearby_salon
                ),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dispatcher.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()


if __name__ == "__main__":
    run_polling()
