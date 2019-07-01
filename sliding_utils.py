# coding = utf-8

# @time    : 2019/7/1 12:12 PM
# @author  : alchemistlee
# @fileName: sliding_utils.py
# @abstract:

import jieba


def sliding_it(input_token,window_size):
  res = []

  if len(input_token)<window_size:
    return res

  base = input_token
  end = len(base)-window_size+1
  for i in range(0,end):
    item=list()
    for j in range(0,window_size):
      real_index = i+j
      item.append(base[real_index])

    item_str =''.join(item)
    if item_str.strip() == '':
      continue
    item_beg =i
    item_end =i+window_size-1
    res.append((item_str,item_beg,item_end))
  return res


def sort_by_beg_pos(sliding_lst):
  def get_beg_pos(item):
    return item[1]

  sliding_lst.sort(key=get_beg_pos)
  return sliding_lst


def filter_overlap(sliding_lst):
  res = list()
  sort_lst = sort_by_beg_pos(sliding_lst)

  need_rm_index =list()
  for i in range(0,len(sort_lst)):
    base = sort_lst[i]
    for j in range(0,len(sort_lst)):
      if i == j:
        continue
      other = sort_lst[j]

      if base[1] == other[1] and base[2]<other[2]:
        need_rm_index.append(i)
        break
      elif other[2] >= base[1] > other[1]:
        need_rm_index.append(i)
        break

  for i in range(0,len(sort_lst)):
    if i in need_rm_index:
      continue
    res.append(sort_lst[i])

  return res


if __name__ == '__main__':
  base = 'Royal Caribbean Cruises Ltd. Q4 adjusted earnings Beat Estimates'
  b1 = "eden hazard's incredible goal against West Ham left Chelsea fans delighted yet devastated as he nears a 100 million move to Real Madrid "
  print(list(jieba.cut(b1)))
  pass
