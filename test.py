#psql 연동 
import psycopg2

conn = psycopg2.connect(host='localhost',dbname='testdb',user='tmclzns',password='ycdc@2020!',port='5432')

cur = conn.cursor()

cur.execute('insert into reputation_indicator(id,indicator_name) values(\'4\',\'file_type\')')

conn.commit()

