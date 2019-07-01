python3 /root/workspace/OpenNMT-py/preprocess.py \
    -train_src /root/workspace/translate_data/my_corpus_v6.zh-cut.processed-v6-.train \
    -train_tgt /root/workspace/translate_data/my_corpus_v6.en.processed-v6-.train \
    -valid_src /root/workspace/translate_data/my_corpus_v6.zh-cut.processed-v6-.val \
    -valid_tgt /root/workspace/translate_data/my_corpus_v6.en.processed-v6-.val \
    -save_data /root/workspace/translate_data/my_corpus_v6_zhen.low \
    -lower -filter_valid -src_seq_length 100 
