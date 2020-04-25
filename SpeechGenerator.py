import json
import requests
import base64


class SpeechGenerator:
    api_key = ""
    url = ""
    headers = ""

    def __init__(self):
        self.api_key = "API_KEY"
        self.url = "https://texttospeech.googleapis.com/v1beta1/text:synthesize?key=" + self.api_key
        self.headers = {'Content-Type': 'application/json; charset=utf-8'}

    def generate_speech_file(self, _text):
        json_data_ = {
            'input': {
                'text': _text
            },
            'voice': {
                'languageCode': 'ja-JP',
                'name': 'ja-JP-Wavenet-A',
                'ssmlGender': 'FEMALE'
            },
            'audioConfig': {
                'audioEncoding': 'MP3'
            }
        }

        jd_ = json.dumps(json_data_)

        s_ = requests.Session()
        r_ = requests.post(self.url, data=jd_, headers=self.headers)

        print("status code : ", r_.status_code)

        if r_.status_code == 200:
            parsed_data_ = json.loads(r_.text)
            with open('data.mp3', 'wb') as f:
                f.write(base64.b64decode(parsed_data_['audioContent']))
