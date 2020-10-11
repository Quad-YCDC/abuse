#psql 연동 
import psycopg2

conn = psycopg2.connect(host='localhost',dbname='testdb1',user='tmclzns',password='ycdc@2020!',port='5432')
cur = conn.cursor()

data_format = '%Y-%m-%d %H:%M:%S'

def reputation_audit_start():
    cur.execute('select url_id from reputation_audit_abuse order by log_date desc limit 1;')
    
    last_urlid = cur.fetchall()
    last_urlid = list(map(int,last_urlid[0]))[0]
    print(type(last_urlid))
    cur.execute('insert into reputation_audit_abuse(audit_log,log_date,url_id) values(\'abuse 수집 시작\' ,now(),%d);'%last_urlid)
    conn.commit()
    return last_urlid
    

last_urlid = reputation_audit_start()
print(last_urlid)

now_date = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
cur.execute('insert into reputation_data(service,indicator_type,indicator,reg_date,cre_date) values(2,1,%s,%s,%s);',(res_csv_json['url'],now_date,res_csv_json['date_added']))