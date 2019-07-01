python3 /root/workspace/OpenNMT-py/translate.py\
    -gpu 6\
    -model ../model_v6_zhen_step_120000.pt\
    -src /root/workspace/translate_data/my_corpus_v6.zh-cut.processed4-v6-filter.test\
    -tgt /root/workspace/translate_data/my_corpus_v6.en.processed4-bpe-v6-filter.test\
    -replace_unk -verbose\
    -output model.v6-zhen-12w.test.pred.atok 
