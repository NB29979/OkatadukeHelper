import json
import requests
import pychromecast


class SpeechGenerator:
    generator_params = {}
    googlehome = None

    def __init__(self, _generator_params):
        self.generator_params = _generator_params

        chromecasts_ = pychromecast.get_chromecasts()
        self.googlehome = next(cc_ for cc_ in chromecasts_ if cc_.device.friendly_name == self.generator_params["googlehome_name"])

    def generate_speech(self, _request_text):
        json_data_ = {
            'api_key':      self.generator_params['tts_api_key'],
            'text':         _request_text,
            'bucket_name':  self.generator_params['gcs_bucket_name'],
            'key_filename': self.generator_params['gcs_key_filename']
        }

        url_ = self.generator_params['gcp_cloud_function_url']
        jd_ = json.dumps(json_data_)
        headers_ = {'Content-Type': 'application/json; charset=utf-8'}

        s_ = requests.Session()
        res_ = requests.post(url_, data=jd_, headers=headers_)

        self.googlehome.wait()
        self.googlehome.media_controller.play_media(res_.text, 'audio.mp3')
        self.googlehome.media_controller.block_until_active()
