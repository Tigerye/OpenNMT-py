#perl /root/workspace/OpenNMT-py/tools/multi-bleu.perl /root/workspace/translate_data/my_corpus_v6.en.processed4-bpe-v6-filter.test.rep-bpe < model.v6-zhen-12w.test.pred.atok.rep-bpe
perl /root/workspace/OpenNMT-py/tools/multi-bleu.perl /root/workspace/translate_data/my_corpus_v6.en.tok.processed6-bpe-v6-2-filter3.test < model.v6-2_zhen-11w.test.pred.atok

perl /root/workspace/OpenNMT-py/tools/multi-bleu.perl /root/workspace/translate_data/my_corpus_v6.en.tok.processed6-bpe-v6-2-filter3.test.unbpe < model.v6-2_zhen-11w.test.pred.atok.unbpe
BLEU = 38.86, 69.1/46.6/35.1/27.6 (BP=0.924, ratio=0.927, hyp_len=5329348, ref_len=5748996)
