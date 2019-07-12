python3 /root/workspace/OpenNMT-py/preprocess.py \
    -train_src /root/workspace/translate_data/my_corpus_v6.en.tok.processed6-bpe-v6-2-.train \
    -train_tgt /root/workspace/translate_data/my_corpus_v6.zh-cut.processed6-bpe-v6-2-.train \
    -valid_src /root/workspace/translate_data/my_corpus_v6.en.tok.processed6-bpe-v6-2-.val \
    -valid_tgt /root/workspace/translate_data/my_corpus_v6.zh-cut.processed6-bpe-v6-2-.val \
    -save_data /root/workspace/translate_data/my_corpus_v6-2_enzh.low \
    -lower -filter_valid 
