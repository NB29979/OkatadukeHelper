# -*- utf-8 -*-
import re
import json
import string
import sqlite3
import datetime
import requests
import pychromecast

import paho.mqtt.client as mqtt

from regex_dict import RegexDict
from CommandInfo import CommandType
from CommandInfo import Command


HOST = "mqtt.beebotte.com"
TOPIC = "[CHANNEL]/[RESOURCE]"
TOKEN = "[TOKEN]"
CACEPT = "mqtt.beebotte.com.pem"
PORT = 8883

okataduke_command_dict = {}

chromecasts = pychromecast.get_chromecasts()
google_home = next(cc for cc in chromecasts if cc.device.friendly_name == [YOUR_GOOGLEHOME_NAME])

def on_connect(_client, _userdata, _flg, _res_code):
    client.subscribe(TOPIC)


def on_message(_client, _userdata, _message):
    recog_result_ = json.loads(_message.payload.decode("utf-8"))["data"].replace(' ', '')
    print('Received result: '+recog_result_)

    try:
        converted_result_ = convert_recog_result_to_command(recog_result_)
        op_ = converted_result_.split(',')
        command_ = Command(op_[0], op_[1:len(op_)])

        conn_ = sqlite3.connect('StrageSpaceDB.sqlite3')
        c_ = conn_.cursor()

        try:
            if command_.type == CommandType.OKATADUKE:
                c_.execute("INSERT INTO storage_space VALUES (?, ?) ON CONFLICT(thing) DO UPDATE SET place = ?;",
                          (command_.operands[0], command_.operands[1], command_.operands[1]))
                conn_.commit()

            elif command_.type == CommandType.WHERE:
                c_.execute("SELECT place FROM storage_space WHERE thing = ?;", (command_.operands[0],))

                request_text_ = c_.fetchall()[0][0]+'です！'
                json_data_ = {
                    'api_key': [YOUR_TTS_API_KEY],
                    'text': request_text_,
                    'bucket_name': [YOUR_BUCKET_NAME_ON_GCS],
                    'key_filename': [YOUR_SERVICE_ACCOUNT_KEY_FILENAME]
                }

                url_ = [YOUR_CLOUD_FUNCTION_URL]
                jd_ = json.dumps(json_data_)
                headers_ = {'Content-Type': 'application/json; charset=utf-8'}

                s_ = requests.Session()
                res_ = requests.post(url_, data=jd_, headers=headers_)

                google_home.wait()
                google_home.media_controller.play_media(res_.text, 'audio.mp3')
                google_home.media_controller.block_until_active()

        except sqlite3.Error as e:
            print('sqlite3 error: ', e.args[0])

        conn_.close()

    except KeyError:
        print('Key error')


def extract_variables(_recog_result):
    words_ = [word_ for word_ in re.findall(r'([一-龥]*[ァ-ー]+|[一-龥]+)', _recog_result) if word_ != '']
    var_dict_ = {}
    if words_:
        for i in range(len(words_)):
            var_dict_['w'+str(i+1)] = words_[i]
    return var_dict_


def convert_recog_result_to_command(_recog_result):
    vars_dict_ = extract_variables(_recog_result)
    selected_command_ = string.Template(okataduke_command_dict[_recog_result])
    return selected_command_.safe_substitute(vars_dict_)


if __name__ == '__main__':
    with open('OkatadukeCommands.json', 'r', encoding='utf-8') as ref_json:
        okataduke_command_dict = RegexDict(json.load(ref_json))

    print('System ready')

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set("token:%s" % TOKEN)
    client.tls_set(CACEPT)
    client.connect(HOST, port=PORT, keepalive=60)
    client.loop_forever()
