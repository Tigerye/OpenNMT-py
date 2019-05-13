# coding = utf-8

# @time    : 2019/5/13 5:15 PM
# @author  : alchemistlee
# @fileName: cut_zh_corpus.py.py
# @abstract:

import jieba

def cut_corpus(in_file):
  out_name = "%s-cut" % in_file
  with open(out_name,'w') as out_fh:
    for line in open(in_file):
      tmp_line = ''.join(line.split())
      tmp_token = list(jieba.cut(tmp_line))
      new_line = ' '.join(tmp_token)
      out_fh.write(new_line+"\n")

  print('finish , [in] = %s , [out] = %s' % (in_file,out_name))


if __name__ == '__main__':
  # a='声音是从他脚边传来的 。 老人低下头 ， 看见了一朵美丽的百合花 。\n'
  # b=''.join(a.split())
  # print(a)
  # print(b)
  # print(list(jieba.cut(a)))
  # print(list(jieba.cut(b)))
  train_f =  ''
  valid_f = ''
  test_f = ''
  cut_corpus(train_f)
  cut_corpus(valid_f)
  cut_corpus(test_f)



