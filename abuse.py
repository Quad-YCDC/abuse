import requests, json
url_id = 'https://urlhaus-api.abuse.ch/v1/urlid/' # urlid 값을 
recent = 'https://urlhaus-api.abuse.ch/v1/urls/recent/limit/1/'
abuse_num = open('./abuse_id.txt','r') # 가장 마지막까지 읽어온 urlid값을 저장
abuse_csv = open('./abuse_csv','a') # urlid값으로 조회한 데이터를 저장

#------------------------------------------
#recent/limit/1로 접속해서 가장 최근에 등록된 정보의 urlid값을 참고함
res_recent = requests.get(recent)
res_recent_json = json.loads(res_recent.text)

for key in res_recent_json['urls']:
    urlid = key['id']
print(urlid)
#------------------------------------------

#------------------------------------------
abuse_urlid = abuse_num.readline() # 마지막으로 조회한 urlid값을 불러옴

params = {'urlid':abuse_urlid} 
res_csv = requests.post(url_id,data=params)
res_csv_json = str(json.loads(res_csv.text))

abuse_csv.write(str(abuse_urlid))
abuse_csv.write('\n')
abuse_csv.write(res_csv_json)
abuse_csv.write('\n')

abuse_num.write(abuse_urlid)
#------------------------------------------ # 이 부분의 urlid값 만큼 반복(추가하면 됨)을 돌리고 urlid값을 abuse_num에 저장


