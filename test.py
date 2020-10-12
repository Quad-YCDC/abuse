import requests, json, datetime
from time import sleep
import psycopg2


url_id = 'https://urlhaus-api.abuse.ch/v1/urlid/'


for urlid_key in range (7999,8000):
    params = {'urlid':urlid_key} 
    res_csv = requests.post(url_id,data=params)
    print(res_csv.text)
    if res_csv.text == '':
        print(1)

    else:
        print(2)
    res_csv_json = json.loads(res_csv.text)