python3 /root/workspace/OpenNMT-py/translate.py \
    -gpu 0 \
    -model ./model_v6-2_enzh_step_170000.pt \
    -src /root/workspace/translate_data/my_corpus_v6.en.tok.processed6-bpe-v6-2-filter3.test \
    -tgt /root/workspace/translate_data/my_corpus_v6.zh-cut.processed6-bpe-v6-2-filter3.test \
    -replace_unk -verbose \
    -output model.v6-2_enzh-17w.test.pred.atok 
