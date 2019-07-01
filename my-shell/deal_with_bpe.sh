sed -r 's/(@@ )|(@@ ?$)//g' model.v6-zhen-12w.test.pred.atok > model.v6-zhen-12w.test.pred.atok.rep-bpe
sed -r 's/(@@ )|(@@ ?$)//g' /root/workspace/translate_data/my_corpus_v6.en.processed4-bpe-v6-filter.test >/root/workspace/translate_data/my_corpus_v6.en.processed4-bpe-v6-filter.test.rep-bpe 
