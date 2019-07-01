python3 /root/workspace/OpenNMT-py/preprocess.py \
    -train_src /root/workspace/translate_data/my_corpus_v6.zh-cut.processed4-v6-.train \
    -train_tgt /root/workspace/translate_data/my_corpus_v6.en.processed4-bpe-v6-.train \
    -valid_src /root/workspace/translate_data/my_corpus_v6.zh-cut.processed4-v6-.val \
    -valid_tgt /root/workspace/translate_data/my_corpus_v6.en.processed4-bpe-v6-.val \
    -save_data /root/workspace/translate_data/my_corpus_v6_zhen.low \
    -lower -filter_valid  
