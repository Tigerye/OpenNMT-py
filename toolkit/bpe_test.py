# coding = utf-8

# @time    : 2019/7/15 3:56 PM
# @author  : alchemistlee
# @fileName: bpe_test.py
# @abstract:

import codecs
from  subword_nmt.apply_bpe import BPE

if __name__ == '__main__':
    print('hi')
    c = codecs.open('/root/workspace/translate_data/my_corpus_v6.zh-cut.processed6-bpe-code', encoding='utf-8')
    m = -1
    sp = '@@'
    voc = None
    a= '保罗 和 哈登'
    bpe = BPE(c, m, sp, voc, None)
    print(bpe.process_line(a))
    pass
