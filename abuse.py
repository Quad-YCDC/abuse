import requests, json, datetime
from time import sleep
import psycopg2

conn = psycopg2.connect(host='localhost',dbname='testdb',user='tmclzns',password='ycdc@2020!',port='5432')

cur = conn.cursor()

url_id = 'https://urlhaus-api.abuse.ch/v1/urlid/' # urlid 값을 
recent = 'https://urlhaus-api.abuse.ch/v1/urls/recent/limit/1/'

#------------------------------------------
#recent/limit/1로 접속해서 가장 최근에 등록된 정보의 urlid값을 참고함
res_recent = requests.get(recent)
res_recent_json = json.loads(res_recent.text)

for key in res_recent_json['urls']:
    urlid = key['id']
print(urlid)
#print(res_recent_json)


test_url_id = 1
for test_url_id in range (1,1000):
    params = {'urlid':test_url_id} 
    res_csv = requests.post(url_id,data=params)
    res_csv_json = json.loads(res_csv.text)
    #print(res_csv.text)
    #print(res_csv_json['date_added'])
    if res_csv_json['query_status'] == "ok":
        if res_csv_json['payloads'] == None:
            print("==========================================")
            print("status :",res_csv_json['query_status'])
            print("url_id :",test_url_id)
            print("url :",res_csv_json['url'])
            print("reg_date :",datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),"UTC")
            print("cre_date :",res_csv_json['date_added'])
            print("response_md5 : NULL")
            print("response_sha256 : NULL")
            print("file_type : NULL")
        
    
        else:
            for payload in res_csv_json['payloads']:
                print("==========================================")
                print("status :",res_csv_json['query_status'])
                print("url_id :",test_url_id)
                print("url :",res_csv_json['url'])
                print("reg_date :",datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),"UTC")
                print("cre_date :",res_csv_json['date_added'])
                print("response_md5 :",payload['response_md5'])
                print("response_sha256 :",payload['response_sha256'])
                print("file_type :",payload['file_type'])
             
        

