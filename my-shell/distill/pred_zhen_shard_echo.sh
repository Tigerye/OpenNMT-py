for i in {1..22}; do
    gpu=0
    echo python3 /root/workspace/OpenNMT-py/translate.py -gpu $gpu -model mycorpus_model_v4_zhen_step_150000.pt -src /root/workspace/translate_data/distill/my_corpus.zh.atok-v4-.train.$i -tgt /root/workspace/translate_data/distill/my_corpus.en.atok-v4-.train.$i -replace_unk -verbose -output /root/workspace/translate_data/distill/my_corpus.en.atok-v4-.train.mycorpus_model_v4_zhen_step_150000.pt.$i
done




