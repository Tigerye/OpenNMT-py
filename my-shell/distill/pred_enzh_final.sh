python3 /root/workspace/OpenNMT-py/translate.py -gpu 7\
    -model /root/workspace/OpenNMT-py/my-shell/mycorpus_model_v4_enzh_distll_step_90000.pt\
    -src /root/workspace/translate_data/my_corpus.en.atok-v4-.test\
    -tgt /root/workspace/translate_data/distill/my_corpus.zh.atok-v4-.test.mycorpus_model_v4_enzh_step_160000.pt\
    -replace_unk -verbose\
    -output /root/workspace/translate_data/distill/my_corpus.en.atok-v4-.test.distill.output

