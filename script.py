import requests
import json
import datetime


SESSION_URL = "https://momkult.jegy.hu/program/lumen-christi-gospel-korus-adventi-koncert-151427/1028954"
TARGET_URL = "https://momkult.jegy.hu/auditview/ticketcount"
# payload
# event_id=1028954&basket=0


def get_session() -> requests.Session:
    return requests.Session()


def get_encoding(response):
    return response.encoding
    
def decode_content(response, encoding):
    return response.content.decode(encoding)
   
def get_contents(response):
    return decode_content(response, get_encoding(response))


# # url = "https://momkult.jegy.hu/auditview/update?audit_id=3395&event_id=1028954&no_sectors=1&initial_data=1&_=1694610456331"
# url = "https://momkult.jegy.hu/auditview/update?audit_id=3395&event_id=1028954&no_sectors=1&initial_data=1"
# response = requests.get(url=url)

# contents = get_contents(response)
# d: dict = json.loads(contents)
# data = d['ticketInitialInfos']
# print(data)



session = get_session()
payload = {
    'event_id': 1028954
}

response = session.post(TARGET_URL,
             data=payload,
             allow_redirects=True
)

content = get_contents(response)
d = json.loads(content)
timestamp = datetime.datetime.now().isoformat()
tickets_left = d['prices']['4000']
row = timestamp + ',' + str(tickets_left)

path_to_file = "outfile.csv"
with open(path_to_file, 'a') as f:
    f.write(row + '\n')