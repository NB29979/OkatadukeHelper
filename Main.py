# -*- utf-8 -*-
import paho.mqtt.client as mqtt
import re
import json
import string
import sqlite3

from regex_dict import RegexDict
from CommandInfo import CommandType
from CommandInfo import Command


HOST = "mqtt.beebotte.com"
TOPIC = "[Channel]/[Resource]"
TOKEN = "[TokenID]"
CACEPT = "mqtt.beebotte.com.pem"
PORT = 8883


okataduke_command_dict = {}


def on_connect(_client, _userdata, _flg, _res_code):
    client.subscribe(TOPIC)


def on_message(_client, _userdata, _message):
    recog_result_ = json.loads(_message.payload.decode("utf-8"))["data"].replace(' ', '')
    print('Received result: '+recog_result_)

    try:
        converted_result_ = convert_recog_result_to_command(recog_result_)
        op_ = converted_result_.split(',')
        command = Command(op_[0], op_[1:len(op_)])

        conn = sqlite3.connect('StrageSpaceDB.sqlite3')
        c = conn.cursor()

        try:
            if command.type == CommandType.OKATADUKE:
                # DBに記録
                c.execute("INSERT INTO storage_space VALUES (?, ?) ON CONFLICT(thing) DO UPDATE SET place = ?;",
                          (command.operands[0], command.operands[1], command.operands[1]))
                conn.commit()

            elif command.type == CommandType.WHERE:
                # DBから読み込み
                c.execute("SELECT place FROM storage_space WHERE thing = ?;", (command.operands[0],))
                for record in c.fetchall():
                    print(record)

        except sqlite3.Error as e:
            print('sqlite3 error: ', e.args[0])

        conn.close()

    except KeyError:
        print('Key error')


def extract_variables(_recog_result):
    words = [word for word in re.findall(r'([一-龥]*[ァ-ー]+|[一-龥]+)', _recog_result) if word != '']
    var_dict_ = {}
    if words:
        for i in range(len(words)):
            var_dict_['w'+str(i+1)] = words[i]
    return var_dict_


def convert_recog_result_to_command(_recog_result):
    vars_dict_ = extract_variables(_recog_result)
    selected_command_ = string.Template(okataduke_command_dict[_recog_result])
    return selected_command_.safe_substitute(vars_dict_)


if __name__ == '__main__':
    with open('OkatadukeCommands.json', 'r', encoding='utf-8') as ref_json:
        okataduke_command_dict = RegexDict(json.load(ref_json))

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set("token:%s" % TOKEN)
    client.tls_set(CACEPT)
    client.connect(HOST, port=PORT, keepalive=60)
    client.loop_forever()
