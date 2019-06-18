# coding = utf-8

# @time    : 2019/6/18 12:02 AM
# @author  : alchemistlee
# @fileName: compare_it_server.py
# @abstract:

from __future__ import unicode_literals

from flask import Flask
from flask import request

import requests
import hashlib
import time
import json

app = Flask(__name__)


def _encrypt(signStr):
  hash_algorithm = hashlib.sha256()
  hash_algorithm.update(signStr.encode('utf-8'))
  return hash_algorithm.hexdigest()


def _truncate(q):
  if q is None:
    return None
  size = len(q)
  return q if size <= 20 else q[0:10] + str(size) + q[size - 10:size]


def get_youdao_res(input,direction = 'zhen'):
  url = 'http://openapi.youdao.com/api'
  app_key = '155783678c10553e'
  passwd = 'VEzzEAXCJi8YuQss8hu7e1JCS8upxoly'
  salt = 'tigerye'

  curtime = str(int(time.time()))

  tmp = app_key + _truncate(input) + salt + curtime + passwd
  sign = _encrypt(tmp)

  print(sign)

  if direction == 'zhen':
    from_str = 'zh-CHS'
    to_str = 'en'
  elif direction == 'enzh':
    from_str = 'EN'
    to_str = 'zh-CHS'

  params = dict()
  params["q"]= input
  params["from"]=from_str
  params["to"]= to_str
  params["sign"]= sign
  params["salt"] = salt
  params["appKey"] = app_key
  params['signType'] = 'v3'

  params['curtime'] = curtime

  print(params)

  headers = {'Content-Type': 'application/x-www-form-urlencoded'}
  r = requests.post(url,headers=headers , data=params)
  res =json.loads(r.text)
  return res['translation']


def get_opennmt_res(input,direction='zhen'):
  enzh_url = 'http://114.80.118.188:5001/translate/en2zh/'
  zhen_url = 'http://114.80.118.188:5000/translate/zh2en/'

  if direction == 'enzh':
    url = enzh_url
  else :
    url = zhen_url

  params = dict()
  params['in'] = input

  headers = {'content-type': 'application/json'}

  r = requests.post(url,headers=headers , data=json.dumps(params))

  res = json.loads(r.text)
  return res['output']


def get_google_res(input, direction = 'zhen'):
  url = 'https://translation.googleapis.com/language/translate/v2'
  key = 'AIzaSyCQKN13Dj4WPTxMphc00DPB0wYyJVEnzOI'

  if direction == 'zhen':
    from_str = 'zh-cn'
    to_str = 'en'
  else :
    from_str = 'en'
    to_str = 'zh-cn'

  params = dict()
  params["target"] = to_str
  params["source"] = from_str
  params["key"] = key
  params["q"] = input

  headers = {'Content-Type': 'application/x-www-form-urlencoded'}

  r = requests.post(url,headers=headers , data=params)
  res = json.loads(r.text)
  res = res['data']
  res = res['translations']
  tmp = res[0]
  res = tmp['translatedText']
  return res


@app.route('/cmp/translate/',methods=['GET','POST'])
def trans_it():
  dir='zhen'
  if request.method == 'POST':
    data = request.get_data()
    json_data = json.loads(data.decode("utf-8"))
    input = json_data['in']
    if 'dir' in json_data:
      dir = json_data['dir']
  else:
    input = request.args.get('in')
    if request.args.get('dir') != None:
      dir = request.args.get('dir')


  youdao_res = get_youdao_res(input,dir)
  opennmt_res = get_opennmt_res(input,dir)
  google_res = get_google_res(input,dir)

  res = {
    'origin':input,
    'youdao': youdao_res,
    'open-nmt':opennmt_res,
    'goog': google_res
  }
  return json.dumps(res,ensure_ascii=False)

if __name__ == '__main__':
  a = 'hello world'
  # b = get_youdao_res(a,'enzh')
  # b = get_google_res(a,'enzh')
  # a= '神评论亮了！'
  # b= get_opennmt_res(a,'zhen')
  # print(b)

  app.debug = True
  app.run(host='0.0.0.0', port=5005)