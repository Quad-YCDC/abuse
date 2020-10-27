import requests, json, datetime
from time import sleep
import psycopg2
from psycopg2 import pool
import urllib3
import configparser
from config import config
import pickle


class List:
    def list_int(self,d):
        return list(d)[0]
    
    def list_str(self,s):
        return list(s)[0]

class Connection_db:
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        threaded_pool = psycopg2.pool.ThreadedConnectionPool(1, 20,**params)
        if(threaded_pool):
            print('DB 연결 성공')
            pool_conn = threaded_pool.getconn()
    except (Exception, psycopg2.DatabaseError) as error:
        print("DB 연결 에러", error)


class Date:
    def Now(self):
        return datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')


class Audit:
    def last_url_id(self):
        Connection_db.cur.execute('select url_id from abuse_url_id order by log_date desc limit 1;')
        last_url_id = Connection_db.cur.fetchone()
        if last_url_id == None:
            print('초기값 설정')
            Connection_db.cur.execute('insert into abuse_url_id(url_id,audit_log,log_date) values(\'1\',\'초기화\',\'%s\');'%Date().Now())
            Connection_db.conn.commit()
            last_url_id = 1
        else:
            last_url_id = last_url_id[0]
        print('last_url_id :',last_url_id)
        return last_url_id
    
    def recent_urlid(self):
        http = urllib3.PoolManager()
        urllib3.disable_warnings()
        recent = 'https://urlhaus-api.abuse.ch/v1/urls/recent/limit/1/'
        #------------------------------------------
        #recent/limit/1로 접속해서 가장 최근에 등록된 정보의 urlid값을 참고함
        res_recent = http.request('GET',recent)
        res_recent_json = json.loads(res_recent.data.decode('utf-8'))

        for key in res_recent_json['urls']:
            urlid = key['id']
        #print(res_recent_json)
        recent_urlid = int(urlid)
        print('recent_url_id:',recent_urlid)
        return recent_urlid


    def loging_start(self):
        print('Abuse.ch 수집 시작')
        Connection_db.cur.execute('insert into reputation_audit(id,audit_log,log_date) values(default,%s,%s);',('Abuse.ch 수집 시작',Date().Now()))
        Connection_db.conn.commit()
    
    def loging_end(self,recent_urlid):
        Connection_db.cur.execute('insert into reputation_audit(audit_log,log_date) values(\'Abuse.ch 수집 종료\',\'%s\');'%Date().Now())
        Connection_db.cur.execute('insert into abuse_url_id(url_id,audit_log,log_date) values(%s,%s,%s);',(recent_urlid,'Abuse.ch 수집 종료 및 url_id 기록',Date().Now()))
        Connection_db.conn.commit()


class Service:
    def indicator_check(self):
        indicator = ['URL','MD5','SHA256','FILE_TYPE']
        for key in indicator:
            Connection_db.cur.execute('select indicator_name from reputation_indicator where indicator_name = \'%s\';'%key)
            check = Connection_db.cur.fetchall()
            check = list(map(str,check[0]))[0]
            if(key != check):
                print('Indicator가 없습니다! 새로운 Indicator를 추가합니다!')
                print('New indicator :',key)
                Connection_db.cur.execute('insert into reputation_indicator(indicator_name) values(\'%s\');'%key)
            else:
                print('Find indicator :',key)

    def indicator_idx(self,indicator_name):
        Connection_db.cur.execute('select id from reputation_indicator where indicator_name = \'%s\';'%indicator_name)
        i = List().list_int(Connection_db.cur.fetchone())
        return i
    
    def indicator_service(self,id):
        Connection_db.cur.execute('select id from reputation_service where service_name = \'%s\';'%id)
        i = List().list_int(Connection_db.cur.fetchone())
        return i

class Crawl:
    Service().indicator_check()
    last_url_id = Audit().last_url_id()
    recent_url_id = Audit().recent_urlid()
    service = Service().indicator_service('abuse')
    indi = ['response_md5','response_sha256','file_type']
    
    url = 'https://urlhaus-api.abuse.ch/v1/urlid/'
    http = urllib3.PoolManager()
    Audit().loging_start()

    for urlid_key in range (last_url_id,recent_url_id):
        params = {'urlid':urlid_key} 
        res_csv = http.request('POST',url,fields=params)
        try:
            res_csv_json = json.loads(res_csv.data.decode('utf-8'))
            if res_csv_json['query_status'] == "ok":
                Connection_db.cur.execute('insert into reputation_data(service,indicator_type,indicator,reg_date,cre_date) values(%s,%s,%s,%s,%s);',(service,Service().indicator_idx('URL'),res_csv_json['url'],Date().Now(),res_csv_json['date_added']))
                Connection_db.conn.commit() 
                print("==========================================")
                print("status :",res_csv_json['query_status'])
                print("url_id :",urlid_key)
                print("url :",res_csv_json['url'])
                
                if res_csv_json['payloads'] == []:
                    print("reg_date :",Date().Now())
                    print("cre_date :",res_csv_json['date_added'])
                    print("response_md5 : NULL")
                    print("response_sha256 : NULL")
                    print("file_type : NULL")
            
                else:
                    for payload in res_csv_json['payloads']:
                        print('payload :',payload)
                        print("reg_date :",Date().Now())
                        print("cre_date :",res_csv_json['date_added'])
                        print("response_md5 :",payload['response_md5'])
                        print("response_sha256 :",payload['response_sha256'])
                        print("file_type :",payload['file_type'])
                        for j in indi:
                            'URL','MD5','SHA256','FILE_TYPE'
                            if j == 'response_md5':
                                a = 'MD5'
                            elif j == 'response_sha256':
                                a = 'SHA256'
                            elif j == 'file_type':
                                a = 'FILE_TYPE'
                            Connection_db.cur.execute('insert into reputation_data(service,indicator_type,indicator,reg_date,cre_date) values(%s,%s,%s,%s,%s);',(service,Service().indicator_idx(a),payload[j],Date().Now(),res_csv_json['date_added']))
                            Connection_db.conn.commit() 
                       
                
        except Exception as error:
            print(urlid_key,'error',error)
            print(type(error))
                  
            

    
    Audit().loging_end(urlid_key)






Connection_db.cur.close()
Connection_db.conn.close()
Connection_db.threaded_pool.putconn(Connection_db.pool_conn)
            













