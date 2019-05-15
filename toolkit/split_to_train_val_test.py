# coding = utf-8

# @time    : 2019/5/11 3:48 PM
# @author  : alchemistlee
# @fileName: split_to_train_val_test.py
# @abstract:

import random


#max_row_number=1172-1
data_size = 22378789
max_row_number = data_size-1

rate = 0.01


def get_rand_rows(size, exclude):
  res = list()
  while True:
    if len(res)>=size:
      break
    selected_row_num = random.randint(0,max_row_number)
    if not selected_row_num in exclude:
      res.append(selected_row_num)
  return res


def produce_train_val_test(in_file,out_train,out_test,out_val,val_rows,test_rows):
  train_fh = open(out_train,'w')
  val_fh = open(out_val,'w')
  test_fh = open(out_test,'w')

  i = 0
  for line in open(in_file):
    if i in val_rows:
      val_fh.write(line)
    elif i in test_rows:
      test_fh.write(line)
    else:
      train_fh.write(line)
    i+=1

  train_fh.close()
  val_fh.close()
  test_fh.close()


def main(in_file_en,in_file_zh,version=None):
  val_size = int(data_size*rate)
  test_size = int(data_size*rate)

  print('val_sample = [ %s ] , test_sample = [ %s ] , all = [ %s ] , rate = [ %s ]' % (str(val_size),str(test_size),str(data_size),str(rate)))

  val_rows = get_rand_rows(val_size,[])
  test_rows = get_rand_rows(test_size,val_rows)
  if version is None:
    train_en=in_file_en+'.train'
    train_zh=in_file_zh+'.train'
    val_en=in_file_en+'.val'
    val_zh=in_file_zh+'.val'
    test_en=in_file_en+'.test'
    test_zh=in_file_zh+'.test'
  else :
    train_en = in_file_en+'-'+version+'-'+'.train'
    train_zh = in_file_zh + '-'+version+'-'+'.train'
    val_en = in_file_en + '-'+version+'-'+'.val'
    val_zh = in_file_zh + '-'+version+'-'+'.val'
    test_en = in_file_en + '-'+version+'-'+'.test'
    test_zh = in_file_zh + '-'+version+'-'+'.test'

  produce_train_val_test(in_file_en,train_en,test_en,val_en,val_rows,test_rows)
  produce_train_val_test(in_file_zh,train_zh,test_zh,val_zh,val_rows,test_rows)
  print("finish it ~")


if __name__ == '__main__':
  in_file_en = '/root/workspace/data/my_corpus.en.atok'
  in_file_zh = '/root/workspace/data/my_corpus.zh.atok'
  main(in_file_en,in_file_zh,version='v4')
