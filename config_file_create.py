from configparser import ConfigParser
config = ConfigParser()

config['local_db'] = {
    'db_host':'localhost',
    'db_name':'testdb1',
    'db_user':'tmclzns',
    'db_password':'ycdc@2020!',
    'db_port':'5432'
}

config['server_db'] = {
    'db_host':'localhost',
    'db_name':'ycdc',
    'db_user':'ycdc',
    'db_password':'ycdc@2020',
    'db_port':'5432'
}

with open('./dev.ini', 'w') as f:
      config.write(f)