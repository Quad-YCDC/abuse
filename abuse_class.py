import requests, json, datetime
from time import sleep
import psycopg2
from psycopg2 import pool
import urllib3
import configparser
from config import config


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


def Now():
    return datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')


class Audit:
    def last_url_id(self):
        Connection_db.cur.execute('select url_id from abuse_url_id order by log_date desc limit 1;')
        last_url_id = Connection_db.cur.fetchone()
        if last_url_id == None:
            print('초기값 설정')
            Connection_db.cur.execute('insert into abuse_url_id(url_id,audit_log,log_date) values(\'1\',\'초기화\',\'%s\');'%Now())
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
        Connection_db.cur.execute('insert into reputation_audit(id,audit_log,log_date) values(default,%s,%s);',('Abuse.ch 수집 시작',now))
        Connection_db.conn.commit()
    
    def loging_end(self,recent_urlid):
        Connection_db.cur.execute('insert into reputation_audit(audit_log,log_date) values(\'Abuse.ch 수집 종료\',\'%s\');'%now)
        Connection_db.cur.execute('insert into abuse_url_id(url_id,audit_log,log_date) values(%s,%s,%s);',(recent_urlid,'Abuse.ch 수집 종료 및 url_id 기록',now))
        Connection_db.conn.commit()


class Service:
    def indicator_check(self):
        indicator = ['URL','MD5','SHA256','FILE_TYPE','REFERENCE']
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
    url = 'https://urlhaus-api.abuse.ch/v1/urlid/'

    Audit().loging_start()

    for urlid_key in range (last_urlid,recent_urlid):
        params = {'urlid':urlid_key} 
        res_csv = http.request('POST',url_id,fields=params)
        try:
            res_csv_json = json.loads(res_csv.data.decode('utf-8'))






Crawl()
Audit().loging_start()
Connection_db.cur.close()
Connection_db.conn.close()
Connection_db.threaded_pool.putconn(Connection_db.pool_conn)
            













