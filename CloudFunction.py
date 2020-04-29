# Function dependencies, for example:
# package>=version
# requests>=2.23.0
# google-cloud-storage>=1.28.0
# oauth2client>=4.1.2

import json
import requests
import urllib
import base64
import time
from datetime import datetime, timedelta
from google.cloud import storage
from oauth2client.service_account import ServiceAccountCredentials


API_ACCESS_ENDPOINT = 'https://storage.googleapis.com'

def main(request):
    request_json = request.get_json()
    api_key = request_json['api_key']
    request_text = request_json['text']
    bucket_name = request_json['bucket_name']
    key_filename = request_json['key_filename']

    # Request for Text to Speech
    url = "https://texttospeech.googleapis.com/v1beta1/text:synthesize?key=" + api_key
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    json_data = {
        'input': {
            'text': request_text
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

    jd = json.dumps(json_data)
    s = requests.Session()
    res = requests.post(url, data=jd, headers=headers)

    if res.status_code == 200:
        # save mp3 file
        parsed_data = json.loads(res.text)
        filename = '/tmp/generated_data' + datetime.now().strftime('%Y%m%d_%H%M%S') + '.mp3'
        with open(filename, 'wb') as f:
            f.write(base64.b64decode(parsed_data['audioContent']))
        
        # upload saved mp3 to GCS
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(filename)
        blob.upload_from_filename(filename)

        # generate signed mp3 url on GCS
        blob = bucket.blob(key_filename)
        json_string = blob.download_as_string()
        key_file_dict = json.loads(json_string)
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(key_file_dict)

        gcs_filename = '/%s/%s' % (bucket_name, filename)
        content_md5, content_type = None, None

        google_access_id = credentials.service_account_email

        expiration = datetime.now() + timedelta(seconds=60)
        expiration = int(time.mktime(expiration.timetuple()))
        
        signature_string = '\n'.join(['GET', content_md5 or '', content_type or '', str(expiration), gcs_filename])
        _, signature_bytes = credentials.sign_blob(signature_string)
        signature = base64.b64encode(signature_bytes)

        query_params = {'GoogleAccessId': google_access_id, 'Expires': str(expiration), 'Signature': signature}

        return '{endpoint}{resource}?{querystring}'.format(endpoint=API_ACCESS_ENDPOINT, resource=gcs_filename, querystring=urllib.parse.urlencode(query_params))
    else:
        return "Error: " + str(res.status_code)
