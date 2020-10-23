import configparser
config = configparser.ConfigParser()
config.read('./dev.ini')

db_conn = config['local_db']
host = db_conn['db_host']
name = db_conn['db_name']
user = db_conn['db_user']
password = db_conn['db_password']
port = db_conn['db_port']




'''
db_conn = 'local_db'

db_host = config.get('db_host',db_conn)
db_name = config.get('db_name',db_conn)
db_user = config.get('db_user',db_conn)
db_password = config.get('db_password',db_conn)
db_port = config.get('db_port',db_conn)

print (db_host)
'''