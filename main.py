# -*- coding: utf8 --
import sqlite3
import telebot
from telebot import types, TeleBot
import datetime
from telebot.types import InlineKeyboardMarkup

import config

conn = sqlite3.connect("data.db")
cursor = conn.cursor()

bot: TeleBot = telebot.TeleBot(config.TOKEN, threaded=False)
def lower(string):
    return str(string).lower()


def insert_varible_into_table_group(id_user, group_name):
    try:
        sqlite_insert_with_param = """INSERT INTO users
                              (id_user, group_name)
                              VALUES (?, ?);"""
        data_tuple = (int(id_user), group_name)
        cursor.execute(sqlite_insert_with_param, data_tuple)
        conn.commit()
        print("Переменные Python успешно вставлены в таблицу users")

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

def insert_varible_into_table_teacher(id_user, FIO):
    try:
        sqlite_insert_with_param = """INSERT INTO users
                              (id_user, FIO)
                              VALUES (?, ?);"""
        data_tuple = (int(id_user), FIO)
        cursor.execute(sqlite_insert_with_param, data_tuple)
        conn.commit()
        print("Переменные Python успешно вставлены в таблицу users")

    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)


lesson_time = {1: '9:00-10:30',
               2: '10:40-12:10',
               3: '12:40-14:10',
               4: '14:20-15:50',
               5: '16:00-17:30',
               6: '18:30-20:00',
               7: '20:10-21:40'}

markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
markup.add('Студент', 'Преподаватель')

def read_lesson_teacher(daynum,weeknum):
    group_name_users = """SELECT lower(FIO) from users where id_user = ?"""
    records = cursor.execute(group_name_users, [id_user]).fetchall()
    sql = 'SELECT * FROM schedule WHERE lower(teacher) = lower(?) AND day_number = ? and week = ? ORDER BY number_lesson'
    num = cursor.execute(sql, [records[0][0], daynum, weeknum]).fetchall()
    print(records[0][0], daynum, weeknum)
    d = {}
    for row in num:
        key = f"{row[1]} {row[2]}"
        if key in d:
            d[key].append(row[0])
        else:
            d[key] = [row[0]]

    if num:
        for row in num:
            key = f"{row[1]} {row[2]}"
            if not d[key]:
                continue
            bot.send_message(id_user, f'<u><b>{row[1]} пара - {lesson_time[row[1]]}:</b></u>\n<b>Предмет:</b> {row[2]}\n<b>Группа(ы):</b> {", ".join(d[key])}\n<b>Формат:</b> {row[3]}\n<b>Аудитория:</b> {row[5]}',parse_mode='html')
            print(f'{row[1]} пара - {lesson_time[row[1]]}:\n{row[2]}\n{", ".join(d[key])}\n{row[3]}\n{row[5]}')
            d[key] = []

        #bot.send_message(message.chat.id, f"http://r.sf-misis.ru/teacher/{num[0][0]}")
    else:
        bot.send_message(id_user, 'Ошибка, попробуйте еще раз')


def read_lesson(daynum,weeknum):
    group_name_users = """SELECT group_name from users where id_user = ?"""
    records = cursor.execute(group_name_users, [id_user]).fetchall()
    sql = 'SELECT * FROM schedule WHERE lower(group_name) = lower(?) AND day_number = ? and week = ? ORDER BY number_lesson'
    num = cursor.execute(sql, [records[0][0], daynum, weeknum]).fetchall()
    print(records[0][0], daynum, weeknum)
    if num:
        for row in num:
            print(row)
            bot.send_message(id_user,
                             f'<u><b>{row[1]} пара - {lesson_time[row[1]]}</b></u>:\n<b>Предмет:</b> {row[2]}\n<b>Препод.:</b> {row[4]}\n<b>Формат: </b>{row[3]}\n<b>Аудитория:</b> {row[5]}',
                             parse_mode='html')
            # bot.send_message(message.chat.id, f"http://r.sf-misis.ru/group/{num[0][0]}")
    else:
        bot.send_message(id_user, 'Ошибка, попробуйте еще раз')

def schedule(id_user,daynum,weeknum):
    try:
        group_name_users = """SELECT group_name from users where id_user = ?"""
        records = cursor.execute(group_name_users, [id_user]).fetchall()
        if records[0][0] != None:
            read_lesson(daynum, weeknum)
        else:
            read_lesson_teacher(daynum, weeknum)
    except:
        bot.register_next_step_handler(id_user, start)

@bot.message_handler(commands=['start'])
def start(message):
    global id_user, markup_1, markup
    print(message.from_user)
    id_user = eval(str(message.from_user))['id']
    group_name_users = """SELECT group_name from users where id_user = ?"""
    records = cursor.execute(group_name_users, [id_user]).fetchall()
    print(records)
    markup_1 = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    item1 = types.KeyboardButton('Расписание')
    markup_1.add(item1)
    if records:
        msg = bot.reply_to(message,  "Привет, {0.first_name}!\nЯ - <b>Помошник</b>, бот созданный, чтобы упростить просмотр расписания ".format(
                             message.from_user, bot.get_me()), parse_mode='html',reply_markup=markup_1)
    else:
        msg = bot.reply_to(message, 'Ты кто?', reply_markup=markup)
        bot.register_next_step_handler(msg, process_choose_step)


def process_choose_step(message):
    post = message.text
    if post == 'Студент':
        msg = bot.reply_to(message, 'Введите номер группы')
        bot.register_next_step_handler(msg, register)
    else:
        markup_2 = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard = True)
        markup_2.add('Цыганков Юрий Александрович', 'Соловьев Антон Юрьевич')
        msg = bot.reply_to(message, 'Введите ФИО', reply_markup=markup_2)
        bot.register_next_step_handler(msg, register)

def register(message):
    post = message.text
    if len(post) > 10:
        insert_varible_into_table_teacher(id_user, post)
    else:
        insert_varible_into_table_group(id_user, post)
    bot.send_message(id_user, 'Поздравляем с регистрацией!', reply_markup=markup_1)

# def process_get_group_step():
#     weeknum = 1 - datetime.date.today().isocalendar()[1] % 2
#     daynum = datetime.date.today().isocalendar()[2]
#     read_lesson(daynum,weeknum)



# def process_get_teacher_step():
#     weeknum = 1 - datetime.date.today().isocalendar()[1] % 2
#     daynum = datetime.date.today().isocalendar()[2]
#     read_lesson_teacher(daynum,weeknum)





# @bot.message_handler(content_types=['text'])
# def main(message):
#     if message.chat.type == 'private':
#         if message.text == 'Расписание':
#             bot.send_message(message.chat.id, "Отдыхай")

@bot.callback_query_handler(func = lambda call: True) #Отвечает за виртуальные кнопки
def callback_woker(call):
    if call.data == 'monday0':
        id_user = eval(str(call.from_user))['id']
        weeknum = 0
        daynum = 1
        schedule(id_user,daynum,weeknum)

@bot.message_handler(content_types = ['text'])
def process_get_main_student(message): #личный кабинет студента
    if message.chat.type == 'private':
        print(message.from_user)
        id_user = eval(str(message.from_user))['id']

        if message.text == 'Расписание':
            #Создаем кнопки с днями недели и передаем их в обработчик
            keyboard0 = types.InlineKeyboardMarkup(row_width = 6)
            monday0 = types.InlineKeyboardButton(text='ПН', callback_data='monday0')
            tuesday0 = types.InlineKeyboardButton(text="ВТ", callback_data='tuesday0')
            wednesday0 = types.InlineKeyboardButton(text='СР', callback_data='wednesday0')
            thrusday0 = types.InlineKeyboardButton(text='ЧТ', callback_data='thrusday0')
            friday0 = types.InlineKeyboardButton(text='ПТ', callback_data='friday0')
            saturday0 = types.InlineKeyboardButton(text='СБ', callback_data='saturday0')
            keyboard0.add(monday0, tuesday0, wednesday0, thrusday0, friday0, saturday0)
            monday1 = types.InlineKeyboardButton(text='ПН', callback_data='monday1')
            tuesday1 = types.InlineKeyboardButton(text="ВТ", callback_data='tuesday1')
            wednesday1 = types.InlineKeyboardButton(text='СР', callback_data='wednesday1')
            thrusday1 = types.InlineKeyboardButton(text='ЧТ', callback_data='thrusday1')
            friday1 = types.InlineKeyboardButton(text='ПТ', callback_data='friday1')
            saturday1 = types.InlineKeyboardButton(text='СБ', callback_data='saturday1')
            keyboard0.add(monday1, tuesday1, wednesday1, thrusday1, friday1, saturday1)
            bot.send_message(message.chat.id, 'На какой день нужно расписание?:', reply_markup=keyboard0)


bot.polling(none_stop=True)