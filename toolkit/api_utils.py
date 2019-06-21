# coding = utf-8

# @time    : 2019/6/20 9:06 PM
# @author  : alchemistlee
# @fileName: api_utils.py
# @abstract:

import json
import requests
import hashlib
import time


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


if __name__ == '__main__':
    pass