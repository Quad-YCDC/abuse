import requests, json, datetime
from time import sleep
import psycopg2
import urllib3
import configparser
config = configparser.ConfigParser()
config.read('./dev.ini')

db_conn = config['local_db']
host = db_conn['db_host']
name = db_conn['db_name']
user = db_conn['db_user']
password = db_conn['db_password']
port = db_conn['db_port']

conn = psycopg2.connect(host=host,
                        dbname=name,
                        user=user,
                        password=password,
                        port=port)

cur = conn.cursor()

http = urllib3.PoolManager()

f = open('./error_log.txt','a')

def get_recent_urlid():
    recent = 'https://urlhaus-api.abuse.ch/v1/urls/recent/limit/1/'
    #------------------------------------------
    #recent/limit/1로 접속해서 가장 최근에 등록된 정보의 urlid값을 참고함
    res_recent = http.request('GET',recent)
    res_recent_json = json.loads(res_recent.data.decode('utf-8'))

    for key in res_recent_json['urls']:
        urlid = key['id']
    #print(res_recent_json)
    recent_urlid = int(urlid)
    print('recenturlid:',recent_urlid)
    return recent_urlid

def search_indicator(indicator):
    cur.execute('select id from reputation_indicator where indicator_name = \'%s\';'%indicator)
    indicator_id = cur.fetchall()
    indicator_id = list(map(int,indicator_id[0]))[0]

    return indicator_id

def indicator_check():
    indicator_name = ['url','md5','sha256','file_type']
    for name in indicator_name:
        cur.execute('select indicator_name from reputation_indicator where indicator_name = \'%s\';'%name)
        name_check = cur.fetchall()
        name_check = list(map(str,name_check[0]))[0]
        print('nameckeck:',name_check)
        if name_check != name:
            cur.execute('insert into reputation_indicator(indicator_name) values (\'%s\');'%name);
            conn.commit()
        else:
            print(name);
        
def reputation_audit_start():
        cur.execute('select url_id from abuse_url_id order by log_date desc limit 1;')
        last_urlid = cur.fetchall()
        if last_urlid == []:
            cur.execute('insert into abuse_url_id(url_id,audit_log,log_date) values(\'1\',\'초기화\',now());');
            conn.commit()
            cur.execute('select url_id from abuse_url_id order by log_date desc limit 1;')
            last_urlid = cur.fetchall()
            last_urlid = list(map(int,last_urlid[0]))[0]
        else:
            cur.execute('select url_id from abuse_url_id order by log_date desc limit 1;')
            last_urlid = cur.fetchall()
            last_urlid = list(map(int,last_urlid[0]))[0]
            print(type(last_urlid))
            cur.execute('insert into reputation_audit(audit_log,log_date) values(\'abuse 수집 시작\' ,now());')
            conn.commit()
            cur.execute('insert into abuse_url_id(url_id,audit_log,log_date) values(%s,%s,now());',(last_urlid,'수집 시작 시간'))
            conn.commit()
        return last_urlid





def reputation_audit_end(recent_urlid):
    cur.execute('insert into reputation_audit(audit_log,log_date) values(\'abuse 수집 종료\',now());')
    cur.execute('insert into abuse_url_id(url_id,audit_log,log_date) values(%s,%s,now());',(recent_urlid,'수집 종료 시간'))

    conn.commit()




url_id = 'https://urlhaus-api.abuse.ch/v1/urlid/'

last_urlid = reputation_audit_start()

recent_urlid = get_recent_urlid()

indicator_check()

for urlid_key in range (last_urlid,recent_urlid):
    params = {'urlid':urlid_key} 
    res_csv = http.request('POST',url_id,fields=params)
    try:
        res_csv_json = json.loads(res_csv.data.decode('utf-8'))
        #print(res_csv.text)
        #print(res_csv_json['date_added'])
        

        if res_csv_json['query_status'] == "ok":
            cur.execute('insert into reputation_data(service,indicator_type,indicator,reg_date,cre_date) values(\'2\',%s,%s,%s,%s);',(search_indicator('URL'),res_csv_json['url'], datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),res_csv_json['date_added']))
            conn.commit()

            print("==========================================")
            print("status :",res_csv_json['query_status'])
            print("url_id :",urlid_key)
            print("url :",res_csv_json['url'])
            
            if res_csv_json['payloads'] == None:
                now_date = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                print("reg_date :",now_date)
                print("cre_date :",res_csv_json['date_added'])
                print("response_md5 : NULL")
                print("response_sha256 : NULL")
                print("file_type : NULL")
        
            else:
                for payload in res_csv_json['payloads']:
                    now_date = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                    print("reg_date :",now_date)
                    print("cre_date :",res_csv_json['date_added'])
                    print("response_md5 :",payload['response_md5'])
                    print("response_sha256 :",payload['response_sha256'])
                    print("file_type :",payload['file_type'])
                    cur.execute('insert into reputation_data(service,indicator_type,indicator,reg_date,cre_date) values(\'2\',%s,%s,%s,%s);',(search_indicator('FileHash-MD5'),payload['response_md5'],now_date,res_csv_json['date_added']))
                    cur.execute('insert into reputation_data(service,indicator_type,indicator,reg_date,cre_date) values(\'2\',%s,%s,%s,%s);',(search_indicator('FileHash-SHA256'),payload['response_sha256'],now_date,res_csv_json['date_added']))
                    cur.execute('insert into reputation_data(service,indicator_type,indicator,reg_date,cre_date) values(\'2\',%s,%s,%s,%s);',(search_indicator('File_type'),payload['file_type'],now_date,res_csv_json['date_added']))
                    conn.commit()
    except Exception as error:
        print(urlid_key,'error')
        print('ex :',ex)

             
reputation_audit_end(urlid_key)


