import requests, json, datetime
from time import sleep
import psycopg2
import urllib3
import configparser

class Psql_conn:
    def Conn(self,location):
        config = configparser.ConfigParser()
        config.read('./dev.ini')
        db_conn = config[location]
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
        return conn

class Reputation:
    def indicator_check(self):
        indicator_list = ['URL','MD5','SHA256','FILE_TYPE','REFERENCE']
        for key in indicator_list:
            cur.execute('select indicator_name from reputation_indicator where indicator_name = \'%s\';'%key)
            a = cur.fetchall()
            if(a != [] and a != key):
                a = list(map(str,a[0]))[0]
                print('Find Indicator :',key)
            else:
                cur.execute('insert into reputation_indicator(indicator_name) values(\'%s\');'%key)
                print("Can't find indicator :",key)
                print("Insert indicator :",key)
                conn.commit()
    

    def audit_start(self):
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
            cur.execute('insert into reputation_audit(audit_log,log_date) values(\'abuse 수집 시작\' ,now());')
            conn.commit()
            cur.execute('insert into abuse_url_id(url_id,audit_log,log_date) values(%s,%s,now());',(last_urlid,'수집 시작 시간'))
            conn.commit()
        print('last_urlid =',last_urlid)
        return last_urlid
    
    def audit_end(self,recent_urlid):
        cur.execute('insert into reputation_audit(audit_log,log_date) values(\'abuse 수집 종료\',now());')
        cur.execute('insert into abuse_url_id(url_id,audit_log,log_date) values(%s,%s,now());',(recent_urlid,'수집 종료 시간'))
        conn.commit()

    def recent_urlid(self):
        http = urllib3.PoolManager()
        recent = 'https://urlhaus-api.abuse.ch/v1/urls/recent/limit/1/'
        #------------------------------------------
        #recent/limit/1로 접속해서 가장 최근에 등록된 정보의 urlid값을 참고함
        res_recent = http.request('GET',recent)
        res_recent_json = json.loads(res_recent.data.decode('utf-8'))

        for key in res_recent_json['urls']:
            urlid = key['id']
        #print(res_recent_json)
        recent_urlid = int(urlid)
        print('recent_urlid:',recent_urlid)
        return recent_urlid

    def indicator_num(self,indicator_name):
        cur.execute('select id from reputation_indicator where indicator_name=\'%s\';'%indicator_name)
        a = cur.fetchall()
        a = list(map(int,a[0]))[0]
        return a



#indicator 값 있는지 확인

Date_Format = '%Y-%m-%d %H:%M:%S'
conn = Psql_conn().Conn('local_db')
cur = conn.cursor()
url_id = 'https://urlhaus-api.abuse.ch/v1/urlid/'
urllib3.disable_warnings()
http = urllib3.PoolManager()

R = Reputation()
chekc = R.indicator_check()
last_urlid = R.audit_start()
#recent_urlid = R.recent_urlid()
indicator_num_url = R.indicator_num('MD5')

urlid_key = 1
params = {'urlid':urlid_key} 
res_csv = http.request('POST',url_id,fields=params)
res_csv_json = json.loads(res_csv.data.decode('utf-8'))


print(res_csv_json['urlhaus_reference'])
        














