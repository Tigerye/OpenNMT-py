# coding = utf-8

# @time    : 2019/7/1 12:13 PM
# @author  : alchemistlee
# @fileName: str_utils.py
# @abstract:

import re
import jieba


def is_alphabet(ch):
  if (ch >= u'\u0041' and ch <= u'\u005a') or (ch >= u'\u0061' and ch <= u'\u007a') :
    return True
  return False

def rm_redundant_space_in_str(input_str):
  tmp_lst = input_str.split()
  res = list()
  for i in range(0,len(tmp_lst)):
    cur = tmp_lst[i]
    next = None

    if i+1 < len(tmp_lst):
      next = tmp_lst[i+1]

    if next is None:
      res.append(cur)
      continue

    cur_end = cur[-1]
    next_beg = next[0]
    if is_alphabet(cur_end) and is_alphabet(next_beg):
      cur+=' '
    res.append(cur)

  return ''.join(res)

def find_all(base_str,tar):
  res = []
  i =0
  while True:
    tar_index = base_str.find(tar,i)
    if tar_index == -1:
      break
    else :
      res.append((tar_index,tar_index+len(tar)))
      i= tar_index+len(tar)
  return res

def re_find_all(base_str,tar):
  pass


def sub_str(base_str ,beg_idx , end_idx, rep_str):
  new = []
  for i in range(0,len(base_str)):
    if i >= beg_idx and i < end_idx:
      continue
    elif i== end_idx:
      new.append(rep_str)
      new.append(base_str[i])
    else:
      new.append(base_str[i])
  return ''.join(new)


def batch_sub_str(base_str,idxs,rep_str):
  last_base_str = base_str
  for item_idx in idxs:
    beg = item_idx[0]
    end = item_idx[1]

    last_base_str = sub_str(last_base_str,beg,end,rep_str)
    print(last_base_str)
  return last_base_str


def is_all_en(input_str):
  for ch in input_str:
    # print(ch)
    if (ch >= u'\u0041' and ch <= u'\u005a') or (ch >= u'\u0061' and ch <= u'\u007a') or (ch == ' '):
      continue
    else:
      return False
  return True


if __name__ == '__main__':
  base = '世界 人民 hello world '
  print(is_all_en(base))
  print(rm_redundant_space_in_str(base))
  # rep = 'wow'
  # beg=2
  # end=6
  #
  # idxs = [(0,1),(5,7)]

  # print(sub_str(base,beg,end,rep))
  # print(batch_sub_str(base,idxs,rep))
  # b= ' 6ProPhase Labs, Inc. is a great company '
  # r1 = re.findall('[^a-z]ProPhase Labs, Inc\.|^ProPhase Labs, Inc\.',b,flags=re.IGNORECASE)
  # print(r1)
  # print(len(r1))
  # t= 'hello '
  # print(t.split())
  # print(list(jieba.cut(t)))
  # print(is_all_en(t))

