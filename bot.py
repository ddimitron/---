from gpt import gpt, count_tokens, clear_history,\
    make_prompt, process_resp, send_request, write_users, users
import logging

import telebot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup

import os
from dotenv import load_dotenv


load_dotenv()
bot = telebot.TeleBot(os.getenv('TOKEN'))

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="log_file.txt",
    filemode="w",
)


def make_keyboard(command_list):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton(command_list))
    return markup


def make_users_json(chat_id):
    if chat_id not in users:
        users[chat_id] = {
            'assistant_content': gpt['assistant_content']
                                  }
        logging.info("A new user has been added to the json file")
        write_users(users)


def reply_prompt(prompt, chat_id, msg):
    request_tokens = count_tokens(prompt)

    if request_tokens > gpt['MAX_TOKENS']:
        bot.send_message(chat_id, "Запрос несоответствует кол-ву "
                                  "токенов. Исправьте запрос: ")
        bot.register_next_step_handler(msg, get_prompt)
        return

    json = make_prompt(prompt, msg)
    resp = send_request(json)
    response = process_resp(resp, msg)

    if not response[0]:
        logging.info("Не удалось выполнить запрос...")
        bot.send_message(chat_id, 'Произошла ошибка, введи запрос заново')
    if response[2] == "":
        bot.send_message(chat_id, 'Объяснение закончено')
    bot.send_message(chat_id, response[2])


@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    keyboard = make_keyboard(['/help', '/solve_task', 'continue'])
    bot.send_message(
        message.chat.id,
        'Привет, дорогой пользователь, я помощник в сфере программирования '
        'на языке python', reply_markup=keyboard
    )
    make_users_json(chat_id)


@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.chat.id, '/solve_task - чтобы задать вопрос '
                                      'нейросети\n'
                                      '/continue - продолжить объяснение ')


@bot.message_handler(commands=['solve_task'])
def solve_task(message):
    chat_id = message.chat.id
    make_users_json(chat_id)
    bot.send_message(message.chat.id, 'Задай вопрос и задачу в '
                                      'следующем сообщение')
    clear_history(message)
    bot.register_next_step_handler(message, get_prompt)


def get_prompt(message):
    if message.content_type != "text":
        mesg = bot.send_message(message.chat.id,
                                "Отправь промпт текстовым сообщением")
        bot.register_next_step_handler(mesg, get_prompt)
        return
    prompt = message.text
    msg = message
    chat_id = message.chat.id
    reply_prompt(prompt, chat_id, msg)


@bot.message_handler(commands=['continue'])
def continue_answer(message):
    chat_id = message.chat.id
    make_users_json(chat_id)
    prompt = users[message.chat.id]['assistant_content']
    if prompt == 'Продолжи объяснение: ':
        bot.send_message(message.chat.id, 'Напиши сначала команду /solve_task')
    msg = message
    reply_prompt(prompt, chat_id, msg)


@bot.message_handler(commands=['debug'])
def password_request(message):
    mesg = bot.send_message(message.chat.id, 'Введите пароль:')
    bot.register_next_step_handler(mesg, send_logs)


def send_logs(message):
    if message.text == os.getenv('PASSWORD'):
        with open("log_file.txt", "rb") as f:
            bot.send_document(message.chat.id, f)
        logging.info('We sent a file with logs')
    else:
        bot.send_message(message.chat.id, 'Пароль неверный')
        logging.info('Someone tried to log in')


bot.infinity_polling()