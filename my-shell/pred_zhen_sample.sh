python3 /root/workspace/OpenNMT-py/translate.py\
    -gpu 7\
    -model mycorpus_model_v4_zhen_step_150000.pt\
    -src /root/workspace/OpenNMT-py/zhen_need_pred.txt-cut\
    -replace_unk -verbose\
    -output zhen_pred_res.txt
