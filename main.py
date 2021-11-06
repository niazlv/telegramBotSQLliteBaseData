import requests
import telebot
import random

from telebot import types

from config import *
from ft_sql import *

bot = telebot.TeleBot(TOKEN)

if DEBUG:
    telebot.logger.setLevel(telebot.logging.DEBUG)

btnexit= types.InlineKeyboardButton("exit", callback_data="delete_message")

#вызывается при команде /start
#   Вызывает кнопки выбора, что дальше делать
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton(text="devInline",callback_data="start_devInline")
    markup.add(btn1)
    markup.add(btnexit)
    bot.send_message(message.chat.id, "Функции", reply_markup=markup)
    bot.send_chat_action(message.chat.id, "typing")

# Вызывается в send_welcome кнопкой devInline
@bot.callback_query_handler(func=lambda call = True: call.data == "start_devInline")
def callback_start_devInline(call):
    telebot.logger.info(call)
    dev_edit_markup_message(call.message)
    bot.answer_callback_query(call.id)

@bot.message_handler(commands=['devInline'])
def dev_edit_markup_message(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("answer", callback_data="dev_answer")
    btn2 = types.InlineKeyboardButton("alert", callback_data="dev_alert")
    markup.add(btn1,btn2)
    markup.add(btnexit)
    bot.send_message(message.chat.id, "callbacks: ", reply_markup=markup)

@bot.callback_query_handler(func=lambda call = True: call.data == "dev_answer")
def callback_dev_answer(call):
    telebot.logger.info(call)
    bot.answer_callback_query(call.id,"ung")
    bot.delete_message(call.message.chat.id,call.message.id)

@bot.callback_query_handler(func=lambda call = True: call.data == "delete_message")
def callback_detele_message(call):
    bot.delete_message(call.message.chat.id, call.message.id)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call = True: call.data == "dev_alert")
def callback_dev_alert(call):
    telebot.logger.info(call)
    bot.answer_callback_query(call.id,"ung",True)
    bot.delete_message(call.message.chat.id,call.message.id)


@bot.message_handler(commands=["sqlexecute"])
def handle_sqlexecute(message):
    mess = message.text
    mess = mess[11:]
    if (len(mess)<1):
        mess = "(none)"
    t = sql_execute(mess)
    bot.send_message(message.chat.id, str(t))

@bot.message_handler(commands=["sql"])
def handle_sql(message):
    mess = message.text
    mess = mess[5:]
    header = "{0}".format(mess)
    header= header.split('\n')[0]
    if ((len(header) < 200) and (len(mess[len(header)+1:])>0)):
        mess = mess[len(header)+1:]
    else:
        header = ""
        bot.send_message(message.chat.id, "Название не обнаружено, либо оно больше 200 символов. Выставлено стандартное", reply_markup=types.InlineKeyboardMarkup().add(btnexit))
    if (len(mess)<1):
        bot.send_message(message.chat.id, "Запрос пустой. Ничего не применено!", reply_markup=types.InlineKeyboardMarkup().add(btnexit))
    else:
        cursor.execute("""
                       INSERT INTO stories (author, author_id, author_username, name, text)
                       VALUES(?,?,?,?,?);
                    """, [""+str(message.from_user.first_name)+" "+ str(message.from_user.last_name),
              int(message.from_user.id),
              str(message.from_user.username),
              str(header),
              mess])
        cursor.execute("""
                        SELECT id FROM stories ORDER BY id DESC LIMIT 1;
        """)
        ft_id = cursor.fetchall()[0][0]
        conn.commit()
        bot.send_message(message.chat.id, "Добавлено под номером "+str(ft_id)+ " в базу знаний!", reply_markup=types.InlineKeyboardMarkup().add(btnexit))

@bot.message_handler(commands="get")
def handle_get(message):
    mess = message.text
    mess = mess[4:]
    if (len(mess)<1):
        bot.send_message(message.chat.id, "Запрос пустой. Введите уникальный индификатор в формате: {0} id".format(message.text[:4]), reply_markup=types.InlineKeyboardMarkup().add(btnexit))
    else:
        cursor.execute("""
                       SELECT * FROM stories WHERE id={0};
        """.format(mess))
        mass = cursor.fetchall()
        conn.commit()
        if (len(mass)>0):
            ft_message = "*{0}* \n".format(mass[0][2])
            ft_message += "{0}\n\n".format(mass[0][3])
            ft_message += "_by author: {0}({1})_".format(mass[0][4],mass[0][6])
            bot.send_message(message.chat.id, ft_message, parse_mode= 'Markdown',reply_markup=types.InlineKeyboardMarkup().add(btnexit))
        else:
            bot.send_message(message.chat.id, "Истории с таким id нет.")
@bot.message_handler(func=lambda m: True)
def echo_all(message):
	bot.reply_to(message, message.text)

@bot.inline_handler(lambda query: query.query)
def query_text(inline_query):
    try:
        r = telebot.types.InlineQueryResultArticle('1', "i love random!) {0}".format(random.randint(0,100)), telebot.types.InputTextMessageContent('/nothing '))
        r2 = telebot.types.InlineQueryResultArticle('2', 'Result2', telebot.types.InputTextMessageContent('Result message2.'))
        bot.answer_inline_query(inline_query.id, [r, r2])
    except Exception as e:
        print(e)

if __name__ == "__main__":
    bot.infinity_polling()