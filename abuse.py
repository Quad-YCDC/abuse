import requests, json, datetime
from time import sleep
import psycopg2

conn = psycopg2.connect(host='localhost',dbname='testdb1',user='tmclzns',password='ycdc@2020!',port='5432')

cur = conn.cursor()


def get_recent_urlid():
    url_id = 'https://urlhaus-api.abuse.ch/v1/urlid/' # urlid 값을 
    recent = 'https://urlhaus-api.abuse.ch/v1/urls/recent/limit/1/'

    #------------------------------------------
    #recent/limit/1로 접속해서 가장 최근에 등록된 정보의 urlid값을 참고함
    res_recent = requests.get(recent)
    res_recent_json = json.loads(res_recent.text)

    for key in res_recent_json['urls']:
        urlid = key['id']
    #print(res_recent_json)
    recent_urlid = int(urlid)
    return recent_urlid


def reputation_audit_start():
    cur.execute('select url_id from reputation_audit_abuse order by log_date desc limit 1;')
    last_urlid = cur.fetchall()
    last_urlid = list(map(int,last_urlid[0]))[0]
    print(type(last_urlid))
    cur.execute('insert into reputation_audit_abuse(audit_log,log_date,url_id) values(\'abuse 수집 시작\' ,now(),%d);'%last_urlid)
    conn.commit()
    return last_urlid




def reputation_audit_end(recent_urlid):
    cur.execute('insert into reputation_audit_abuse(audit_log,log_date,url_id) values(\'abuse 수집 종료\' ,now(),%d);'%recent_urlid)
    conn.commit()




url_id = 'https://urlhaus-api.abuse.ch/v1/urlid/'

last_urlid = reputation_audit_start()

recent_urlid = get_recent_urlid()

for urlid_key in range (last_urlid,recent_urlid):
    params = {'urlid':urlid_key} 
    res_csv = requests.post(url_id,data=params)
    res_csv_json = json.loads(res_csv.text)
    #print(res_csv.text)
    #print(res_csv_json['date_added'])
    

    if res_csv_json['query_status'] == "ok":
        cur.execute('insert into reputation_data(service,indicator_type,indicator,reg_date,cre_date) values(\'2\',\'1\',%s,%s,%s);',(res_csv_json['url'], datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),res_csv_json['date_added']))
        conn.commit()

        if res_csv_json['payloads'] == None:
            now_date = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            print("==========================================")
            print("status :",res_csv_json['query_status'])
            print("url_id :",urlid_key)
            print("url :",res_csv_json['url'])
            print("reg_date :",now_date)
            print("cre_date :",res_csv_json['date_added'])
            print("response_md5 : NULL")
            print("response_sha256 : NULL")
            print("file_type : NULL")
            cur.execute('insert into reputation_data(service,indicator_type,indicator,reg_date,cre_date) values(\'2\',\'2\',%s,%s,%s);',(payload['response_md5'],now_date,res_csv_json['date_added']))
            cur.execute('insert into reputation_data(service,indicator_type,indicator,reg_date,cre_date) values(\'2\',\'3\',%s,%s,%s);',(payload['response_sha256'],now_date,res_csv_json['date_added']))
            conn.commit()
    
        else:
            for payload in res_csv_json['payloads']:
                now_date = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                print("==========================================")
                print("status :",res_csv_json['query_status'])
                print("url_id :",urlid_key)
                print("url :",res_csv_json['url'])
                print("reg_date :",now_date)
                print("cre_date :",res_csv_json['date_added'])
                print("response_md5 :",payload['response_md5'])
                print("response_sha256 :",payload['response_sha256'])
                print("file_type :",payload['file_type'])
                cur.execute('insert into reputation_data(service,indicator_type,indicator,reg_date,cre_date) values(\'2\',\'2\',%s,%s,%s);',(payload['response_md5'],now_date,res_csv_json['date_added']))
                cur.execute('insert into reputation_data(service,indicator_type,indicator,reg_date,cre_date) values(\'2\',\'3\',%s,%s,%s);',(payload['response_sha256'],now_date,res_csv_json['date_added']))
                conn.commit()
             
reputation_audit_end(urlid_key)

