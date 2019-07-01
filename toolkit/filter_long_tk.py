# coding = utf-8

# @time    : 2019/6/30 6:41 PM
# @author  : alchemistlee
# @fileName: filter_long_tk.py
# @abstract:

if __name__ == '__main__':

    input_zh = '/root/workspace/translate_data/my_corpus_v6.zh-cut.processed4-v6-.test'
    input_en = '/root/workspace/translate_data/my_corpus_v6.en.processed4-bpe-v6-.test'

    out_zh = '/root/workspace/translate_data/my_corpus_v6.zh-cut.processed4-v6-filter.test'
    out_en = '/root/workspace/translate_data/my_corpus_v6.en.processed4-bpe-v6-filter.test'

    with open(input_zh,'r') as i_zh, open(input_en,'r') as i_en, open(out_zh,'w') as o_zh, open(out_en, 'w') as o_en:
        for row_zh, row_en in zip(i_zh, i_en):
            zh_toks = row_zh.split()

            if len(zh_toks) > 200:
                continue

            o_zh.write(row_zh.strip()+'\n')
            o_en.write(row_en.strip()+'\n')


