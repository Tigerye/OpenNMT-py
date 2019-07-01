python3 /root/workspace/OpenNMT-py/translate.py -gpu 0 -model /root/workspace/OpenNMT-py/my-shell/mycorpus_model_v4_zhen_step_150000.pt -src /root/workspace/OpenNMT-py/my-shell/sentiment/sentiment_test_set_p/1/negative_zh -tgt /root/workspace/OpenNMT-py/my-shell/sentiment/sentiment_test_set_p/1/negative_zh -verbose -output /root/workspace/OpenNMT-py/my-shell/sentiment/sentiment_test_set_p/1/negative_en
python3 /root/workspace/OpenNMT-py/translate.py -gpu 0 -model /root/workspace/OpenNMT-py/my-shell/mycorpus_model_v4_zhen_step_150000.pt -src /root/workspace/OpenNMT-py/my-shell/sentiment/sentiment_test_set_p/1/positive_zh -tgt /root/workspace/OpenNMT-py/my-shell/sentiment/sentiment_test_set_p/1/positive_zh -replace_unk -verbose -output /root/workspace/OpenNMT-py/my-shell/sentiment/sentiment_test_set_p/1/positive_en

python3 /root/workspace/OpenNMT-py/translate.py -gpu 0 -model /root/workspace/OpenNMT-py/my-shell/mycorpus_model_v4_zhen_step_150000.pt -src /root/workspace/OpenNMT-py/my-shell/sentiment/sentiment_test_set_p/2/negative_zh -tgt /root/workspace/OpenNMT-py/my-shell/sentiment/sentiment_test_set_p/2/negative_zh -replace_unk -verbose -output /root/workspace/OpenNMT-py/my-shell/sentiment/sentiment_test_set_p/2/negative_en
python3 /root/workspace/OpenNMT-py/translate.py -gpu 0 -model /root/workspace/OpenNMT-py/my-shell/mycorpus_model_v4_zhen_step_150000.pt -src /root/workspace/OpenNMT-py/my-shell/sentiment/sentiment_test_set_p/2/positive_zh -tgt /root/workspace/OpenNMT-py/my-shell/sentiment/sentiment_test_set_p/2/positive_zh -replace_unk -verbose -output /root/workspace/OpenNMT-py/my-shell/sentiment/sentiment_test_set_p/2/positive_en


python3 /root/workspace/OpenNMT-py/translate.py -gpu 0 -model /root/workspace/OpenNMT-py/my-shell/mycorpus_model_v4_zhen_step_150000.pt -src /root/workspace/OpenNMT-py/my-shell/sentiment/sentiment_test_set_p/3/negative_zh -tgt /root/workspace/OpenNMT-py/my-shell/sentiment/sentiment_test_set_p/3/negative_zh -replace_unk -verbose -output /root/workspace/OpenNMT-py/my-shell/sentiment/sentiment_test_set_p/3/negative_en
python3 /root/workspace/OpenNMT-py/translate.py -gpu 0 -model /root/workspace/OpenNMT-py/my-shell/mycorpus_model_v4_zhen_step_150000.pt -src /root/workspace/OpenNMT-py/my-shell/sentiment/sentiment_test_set_p/3/positive_zh -tgt /root/workspace/OpenNMT-py/my-shell/sentiment/sentiment_test_set_p/3/positive_zh -replace_unk -verbose -output /root/workspace/OpenNMT-py/my-shell/sentiment/sentiment_test_set_p/3/positive_en

















#python3 /root/workspace/OpenNMT-py/translate.py -gpu 0 -model /root/workspace/OpenNMT-py/my-shell/mycorpus_model_v4_zhen_distll_step_120000.pt -src /root/workspace/OpenNMT-py/my-shell/sentiment/sentiment_test_set_p/1/negative_zh -tgt /root/workspace/OpenNMT-py/my-shell/sentiment/sentiment_test_set_p/1/negative_zh -replace_unk -verbose -output /root/workspace/OpenNMT-py/my-shell/sentiment/sentiment_test_set_p/1/negative_en_distill
