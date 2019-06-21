# coding = utf-8

# @time    : 2019/6/20 3:52 PM
# @author  : alchemistlee
# @fileName: scan_corpus.py
# @abstract:

import os
from api_utils import get_youdao_res, logging
import Levenshtein
import random
import numpy as np
import time


def load_corpus_file(catalog_file):
  res = dict()
  for line in open(catalog_file,'r'):
    line = line.strip()
    dir = os.path.dirname(line)
    filename = os.path.basename(line)
    suffix = os.path.splitext(filename)
    suffix = suffix[-1].strip('.')
    print('path = {} , filename = {} , suffix = {} '.format(dir,filename,suffix))
    if not dir in res.keys():
      tmp_dict = dict()
      tmp_dict[suffix] = filename
      res[dir] = tmp_dict
    else :
      tmp_dict = res[dir]
      tmp_dict[suffix] = filename
      res[dir] = tmp_dict
  return res


def get_distance(l, r):
  return Levenshtein.ratio(l,r)


def get_baseline(input):
  return get_youdao_res(input,direction='zhen')


def random_sample(en_file, zh_file, rate):
  selected_idx = list()
  zh_sample = list()
  en_sample = list()

  index = 0
  for line in open(zh_file):
    line = line.strip()
    if random.random() <= rate:
      zh_sample.append(line)
      selected_idx.append(index)
    index+=1

  doc_cnt = index+1

  index = 0
  for line in open(en_file):
    line = line.strip()
    if index in selected_idx:
      en_sample.append(line)
    index +=1

  return zh_sample, en_sample, doc_cnt


def summary_score(scores,doc_cnt):
  if len(scores) == 0:
    print('score is empty ! ')
    return

  avg_score = np.mean(scores)
  mid_score = np.median(scores)
  good_score_cnt = 0
  for s in scores:
    if s >= 0.6:
      good_score_cnt +=1
  return avg_score, mid_score, good_score_cnt/doc_cnt


def main(catalog_file, log_file):
  all_corpus = load_corpus_file(catalog_file)

  with open(log_file,'w') as log_fh:
    for dir in all_corpus.keys():
      tmp_info = all_corpus[dir]
      en_file = tmp_info['en']
      zh_file = tmp_info['zh']

      logging(log_fh, 'dir = {}'.format(dir))
      logging(log_fh, 'en = {} , zh = {}'.format(en_file,zh_file))

      tmp_en = dir + '/'+ en_file
      tmp_zh = dir + '/'+ zh_file

      zh_sample, en_sample, doc_size = random_sample(tmp_en, tmp_zh, 0.001)

      assert len(zh_sample) == len(en_sample)

      scores = []
      logging(log_fh, 'sample-size = {} , doc-size = {} '.format(len(zh_sample),doc_size))
      for i in range(len(zh_sample)):
        zh_line = zh_sample[i]
        en_line = en_sample[i]
        baseline_en = get_youdao_res(zh_line)
        time.sleep(1)
        if baseline_en is None:
          continue

        baseline_en = baseline_en[0]

        sim_score = get_distance(baseline_en, en_line)
        print('base = {} , ori = {}'.format(baseline_en, en_line))
        print('score = {}'.format(str(sim_score)))
        scores.append(sim_score)

      avg, mid, good_per = summary_score(scores, doc_size)
      logging(log_fh, 'avg = {} , mid = {} , good_per = {} '.format(avg, mid, good_per))


if __name__ == '__main__':
  main(catalog_file='/root/workspace/translate_data/corpus_file_list',log_file='/root/workspace/translate_data/corpus.log')
