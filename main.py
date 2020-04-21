# -*- utf-8 -*-
import paho.mqtt.client as mqtt
import re
import json

from regex_dict import  RegexDict


HOST = "mqtt.beebotte.com"
TOPIC = "[Channel]/[Resource]"
TOKEN = "[Token]"
CACEPT = "mqtt.beebotte.com.pem"
PORT = 8883

okataduke_command_dict = {}


def on_connect(_client, _userdata, _flg, _res_code):
    client.subscribe(TOPIC)


def on_message(_client, _userdata, _message):
    recog_result_ = json.loads(_message.payload.decode("utf-8"))["data"].replace(' ', '')
    print('Received result: '+recog_result_)

    try:
        pass
    except KeyError:
        print('Key error')


def convert_recog_result_to_command():
    pass


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
