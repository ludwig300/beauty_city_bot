import logging
import os

import django

from math import asin, cos, radians, sin, sqrt
from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
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
NEARBY_SALON = 2
MASTER = 3
SERVICE = 4
SCHEDULE = 5
TIME = 6
AGREEMENT = 7
NAME = 8
PHONE = 9
REGISTRATION = 10
CONFIRMATION = 11
SALONS = 12
END = ConversationHandler.END


def registration(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [['Согласен', 'Не согласен']]
    user = update.message.from_user
    logger.info("Master of %s: %s", user.first_name, update.message.text)
    update.message.reply_text(
        'Привет, мы собираем личные данные. Вы согласны на обработку вашей персональной информации?',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True,
            resize_keyboard=True,
            input_field_placeholder='Нажми Согласен=))'
        ),
    )

    return AGREEMENT


def agreement(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Agreement of %s: %s", user.first_name, update.message.text)
    update.message.reply_text(
        'Пожалуйста, укажите ваше имя',
        reply_markup=ReplyKeyboardRemove(),
    )

    return NAME


def name(update: Update, context: CallbackContext) -> int:
    try:
        user = update.message.from_user
        if not user:
            raise ValueError('Invalid value')
        logger.info("Name of %s: %s", user.first_name, update.message.text)
        context.bot_data['name'] = update.message.text
        update.message.reply_text(
            'Прекрасно. Теперь напишите ваш номер телефона'
        )
    except ValueError:
        print('Вы не указали ваше имя.')

    return PHONE


def phone_number(update: Update, context: CallbackContext) -> int:
    context.bot_data['phone'] = update.message.text
    reply_keyboard = [['Хочу записаться!', 'Отменить']]
    try:
        user = update.message.from_user
        if not user:
            raise ValueError('Invalid value')
        logger.info("Email of %s: %s", user.first_name, update.message.text)
        update.message.reply_text(
            'Спасибо. Подтвердите запись к мастеру',
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True,
                resize_keyboard=True,
            )
        )
    except ValueError:
        print('Похоже, что во введённом вами адресе электронной почты есть ошибка.')

    return CONFIRMATION


def confirmation(update: Update, context: CallbackContext) -> int:
    print(context.bot_data)
    user = update.message.from_user
    reply_keyboard = [['Оплатить сейчас']]
    update.message.reply_text(
        'Спасибо. Вы записаны',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True,
            resize_keyboard=True,
        )
    )


def dist_between_two_lat_lon(*args):
    lat1, lat2, long1, long2 = map(radians, args)

    dist_lats = abs(lat2 - lat1)
    dist_longs = abs(long2 - long1)
    a = sin(dist_lats / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dist_longs / 2) ** 2
    c = asin(sqrt(a)) * 2
    radius_earth = 6378
    return c * radius_earth


def find_closest_lat_lon(data, v):
    try:
        return min(
            data,
            key=lambda p: dist_between_two_lat_lon(
                v['latitude'], p['latitude'], v['longitude'], p['longitude']
            )
        )
    except TypeError:
        print('Not a list or not a number.')


def start(update: Update, context: CallbackContext) -> int:
    reply_keyboard = [
        ['Выбрать салон', 'Выбрать мастера', 'Выбрать услугу'],
        ['Отменить']
    ]
    context.bot_data['step'] = 1
    print('start, step:', context.bot_data['step'])
    user = update.message.from_user
    logger.info("Choice of %s: %s", user.first_name, update.message.text)
    update.message.reply_text(
        'Привет, давай наведем тебе красоту.\n Можешь выбрать ближайший салон, любимого мастера или услугу.',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True,
            resize_keyboard=True,
        ),
    )

    return START_CHOICE


def show_salons(update: Update, context: CallbackContext) -> int:
    user = update.message.location
    salons = Salon.objects.all()
    salons_buttons = list()
    context.bot_data['step'] += 1
    print('show_salons, step:', context.bot_data['step'])
    for salon in salons:
        logger.info(
            "Agreement of %s, %s: > Salon location: %s, %s",
            salon,
            user,
            salon.lon,
            salon.lat
        )
        salons_buttons.append([salon.salon_name])
    print(salons_buttons)
    update.message.reply_text(
        'Выберите салон',
        reply_markup=ReplyKeyboardMarkup(
            salons_buttons, one_time_keyboard=True,
            resize_keyboard=True,
        )
    )
    return SERVICE


def nearby_salon(update: Update, context: CallbackContext) -> int:
    user = update.message.location
    context.bot_data['step'] += 1
    print('nearby_salon, step:', context.bot_data['step'])
    salons = Salon.objects.all()
    salons_location = list()
    for salon in salons:
        logger.info(
            "Agreement of %s, %s: > Salon location: %s, %s",
            salon,
            user,
            salon.lon,
            salon.lat
        )
        salons_location.append({'latitude': salon.lat, 'longitude': salon.lon})
    nearby_location = find_closest_lat_lon(salons_location, user)
    salon = salons.filter(
        lat=nearby_location['latitude'],
        lon=nearby_location['longitude']
    ).first()

    context.bot_data['salon'] = [salon.salon_name, salon.address]
    reply_keyboard = [['Выбрать услугу']]
    update.message.reply_text(
        f' Ближайший салон: {salon.salon_name}',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True,
            resize_keyboard=True,
        )
    )
    return SERVICE


def master(update: Update, context: CallbackContext) -> int:
    reply_keyboard = list()
    context.bot_data['step'] += 1
    print('master, step:', context.bot_data['step'])
    specialists = Specialist.objects.all()
    for some_specialist in specialists:
        reply_keyboard.append(
            [some_specialist.full_name]
        )
    user = update.message.from_user
    logger.info("Master choice of %s: %s", user.first_name, reply_keyboard)
    logger.info("Time of %s: %s", user.first_name, update.message.text)
    update.message.reply_text(
        'Выберите мастера',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True,
            resize_keyboard=True,
        ),
    )
    if context.bot_data['step'] == 2:
        return SALONS
    elif context.bot_data['step'] == 6:
        return REGISTRATION


def service(update: Update, context: CallbackContext) -> int:
    reply_keyboard = list()
    context.bot_data['step'] += 1
    print('service, step:', context.bot_data['step'])
    services = Service.objects.all()
    for some_service in services:
        reply_keyboard.append(
            [f'{some_service.service_name} {some_service.price}']
        )
    user = update.message.from_user
    logger.info("Service choice of %s: %s", user.first_name, reply_keyboard)
    update.message.reply_text(
        'Выберите услугу',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True,
            resize_keyboard=True,
        ),
    )

    return TIME


def time(update: Update, context: CallbackContext) -> int:
    reply_keyboard = list()
    context.bot_data['step'] += 1
    print('time, step:', context.bot_data['step'])
    booking_time = Schedule.objects.all()
    for some_time in booking_time:
        reply_keyboard.append(
            [some_time.TIMESLOT_LIST]
        )
    user = update.message.from_user
    logger.info("Service of %s: %s", user.first_name, update.message.text)
    context.bot_data['service'] = update.message.text
    update.message.reply_text(
        'Выберите время',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True,
            resize_keyboard=True,
        ),
    )

    return MASTER


def location(update: Update, context: CallbackContext) -> int:
    location_keyboard = KeyboardButton(
        text='Поделиться локацией',
        request_location=True
    )
    context.bot_data['step'] += 1
    print('location, step:', context.bot_data['step'])
    custom_keyboard = [[location_keyboard]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
    update.message.reply_text(
        text="Чтобы найти ближайшие салоны, поделитесь своей геолокацией",
        reply_markup=reply_markup
    )
    return NEARBY_SALON


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
                ),
                MessageHandler(
                    Filters.regex('^Отменить$'),
                    cancel
                )
            ],
            NEARBY_SALON: [
                MessageHandler(
                    Filters.location,
                    nearby_salon
                ),
            ],
            SALONS: [
                MessageHandler(
                    Filters.text & ~Filters.command,
                    show_salons
                ),
            ],
            MASTER: [
                MessageHandler(
                    Filters.text & ~Filters.command,
                    master
                ),
            ],
            SERVICE: [
                MessageHandler(
                    Filters.text & ~Filters.command,
                    service
                )
            ],
            TIME: [
                MessageHandler(
                    Filters.text & ~Filters.command,
                    time
                )
            ],
            REGISTRATION: [
                MessageHandler(
                    Filters.text & ~Filters.command,
                    registration
                )
            ],
            AGREEMENT: [
                MessageHandler(
                    Filters.regex('^Согласен$'),
                    agreement
                ),
                MessageHandler(
                    Filters.regex('^Не согласен$'),
                    cancel
                )
            ],
            NAME: [MessageHandler(Filters.text & ~Filters.command, name)],
            PHONE: [MessageHandler(Filters.text & ~Filters.command, phone_number)],
            CONFIRMATION: [
                MessageHandler(
                    Filters.regex('^Хочу записаться!$'),
                    confirmation
                ),
                MessageHandler(
                    Filters.regex('^Отменить$'),
                    cancel
                )
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dispatcher.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()


if __name__ == "__main__":
    run_polling()
