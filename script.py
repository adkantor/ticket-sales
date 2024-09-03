import requests
import json
import datetime


SESSION_URL = "https://momkult.jegy.hu/program/lumen-christi-gospel-korus-adventi-koncert-151427/1176162"
TARGET_URL = "https://momkult.jegy.hu/auditview/ticketcount"

PATH_TO_OUTFILE = "outfile.json"


def get_session() -> requests.Session:
    return requests.Session()


def get_encoding(response):
    return response.encoding
    
def decode_content(response, encoding):
    return response.content.decode(encoding)
   
def get_contents(response):
    return decode_content(response, get_encoding(response))


session = get_session()
payload = {
    'event_id': 1176162
}

response = session.post(TARGET_URL,
             data=payload,
             allow_redirects=True
)

content = get_contents(response)
d = json.loads(content)

try:
    with open(PATH_TO_OUTFILE, 'r') as f:
        data = json.load(f)
except:
    data = []

timestamp = datetime.datetime.now().isoformat()

data_item = {
    'timestamp': timestamp,
    'data': d,
}
data.append(data_item)

with open(PATH_TO_OUTFILE, 'w') as f:
    json.dump(data, f, indent=4)