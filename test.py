import requests, json, datetime
from time import sleep
import psycopg2
from psycopg2 import pool
import urllib3
import configparser
from config import config
import pickle


http = urllib3.PoolManager()
url = 'https://urlhaus-api.abuse.ch/v1/urlid/'
urlid_key = 826
params = {'urlid':urlid_key} 
res_csv = http.request('POST',url,fields=params)
res_csv_json = json.loads(res_csv.data.decode('utf-8'))
print(res_csv_json)