# -*- coding: utf8 --
import sqlite3
import telebot
from telebot import types, TeleBot

import config

conn = sqlite3.connect("data.db")
cursor = conn.cursor()

bot: TeleBot = telebot.TeleBot(config.TOKEN, threaded=False)


@bot.message_handler(commands=['start'])
def start(message):
    print(message.from_user)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Студент', 'Преподаватель')
    msg = bot.reply_to(message, 'Ты кто?', reply_markup=markup)
    bot.register_next_step_handler(msg, process_choose_step)


def process_choose_step(message):
    post = message.text
    if post == 'Студент':
        msg = bot.reply_to(message, 'Введите номер группы')
        bot.register_next_step_handler(msg, process_get_group_step)
    else:
        msg = bot.reply_to(message, 'Введите ФИО')
        bot.register_next_step_handler(msg, process_get_teacher_step)


def process_get_group_step(message):
    sql = 'SELECT href FROM groups WHERE group_name = ?'
    num = cursor.execute(sql, [message.text]).fetchall()

    if num:
        bot.send_message(message.chat.id, f"http://r.sf-misis.ru/group/{num[0][0]}")
    else:
        msg = bot.reply_to(message, 'Ошибка, попробуйте еще раз')
        bot.register_next_step_handler(msg, process_get_group_step)


def process_get_teacher_step(message):
    sql = 'SELECT href FROM teachers WHERE FIO = ?'
    num = cursor.execute(sql, [message.text]).fetchall()

    if num:
        bot.send_message(message.chat.id, f"http://r.sf-misis.ru/teacher/{num[0][0]}")
    else:
        msg = bot.reply_to(message, 'Ошибка, попробуйте еще раз')
        bot.register_next_step_handler(msg, process_get_teacher_step)


# @bot.message_handler(content_types=['text'])
# def main(message):
#     if message.chat.type == 'private':
#         if message.text == 'Расписание':
#             bot.send_message(message.chat.id, "Отдыхай")

bot.polling(none_stop=True)
