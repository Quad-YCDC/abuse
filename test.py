import urllib3
import requests,json

http = urllib3.PoolManager()
url_id = 'https://urlhaus-api.abuse.ch/v1/urlid/'

urlid_key = 10
params = {'urlid':urlid_key} 
res = http.request('POST',url_id,fields=params)

print(res.data.decode('utf-8'))