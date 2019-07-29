# prepare data

## step 1 - corpus
###1. tok
    zh : jieba分词 -> tok
    en : tok

    perl /root/workspace/dl4mt-tutorial/data/tokenizer.perl -l en < /root/workspace/translate_data/my_corpus_v6.en > /root/workspace/translate_data/my_corpus_v6.en.tok

###2. replace entity(could also replace number and units)
    python /root/workspace/OpenNMT-py/new_trans_preproc.py 0 25000000 /root/workspace/translate_data/my_corpus_v6.zh-cut /root/workspace/translate_data/my_corpus_v6.en.tok

###3. bpe
    3.1 learn bpe
        subword-nmt learn-bpe -s 50000 < /root/workspace/translate_data/my_corpus_v6.en.tok.processed7  > /root/workspace/translate_data/my_corpus_v6.en.tok.processed7-bpe-code
        subword-nmt learn-bpe -s 50000 < /root/workspace/translate_data/my_corpus_v6.zh-cut.processed7  > /root/workspace/translate_data/my_corpus_v6.zh-cut.processed7-bpe-code
    3.2 apply bpe
        subword-nmt apply-bpe -c  /root/workspace/translate_data/my_corpus_v6.en.tok.processed7-bpe-code < /root/workspace/translate_data/my_corpus_v6.en.tok.processed7  > /root/workspace/translate_data/my_corpus_v6.en.tok.processed7-bpe
        subword-nmt apply-bpe -c  /root/workspace/translate_data/my_corpus_v6.zh-cut.processed7-bpe-code < /root/workspace/translate_data/my_corpus_v6.zh-cut.processed7  > /root/workspace/translate_data/my_corpus_v6.zh-cut.processed7-bpe

## step 2 - train & evaluate

###1. split data_set
    edit the script toolkit/split_to_train_val_test.py

###2. process
    python3 /root/workspace/OpenNMT-py/preprocess.py \
    -train_src /root/workspace/translate_data/my_corpus_v6.en.tok.processed7-bpe-v6-2-.train \
    -train_tgt /root/workspace/translate_data/my_corpus_v6.zh-cut.processed7-bpe-v6-2-.train \
    -valid_src /root/workspace/translate_data/my_corpus_v6.en.tok.processed7-bpe-v6-2-.val \
    -valid_tgt /root/workspace/translate_data/my_corpus_v6.zh-cut.processed7-bpe-v6-2-.val \
    -save_data /root/workspace/translate_data/my_corpus_v6-2_enzh2.low \
    -filter_valid -src_vocab_size 50100 -tgt_vocab_size 50100 -src_seq_length 100 -tgt_seq_length 100

###3. train model
    CUDA_VISIBLE_DEVICES=3,4,5,7 python3 /root/workspace/OpenNMT-py/train.py\
    -data /root/workspace/translate_data/my_corpus_v6-2_enzh2.low\
    -save_model model_v6-2_enzh2\
    -layers 6 -rnn_size 512 -word_vec_size 512 -transformer_ff 2048 -heads 8  -encoder_type transformer -decoder_type transformer -position_encoding   -train_steps 200000  -max_generator_batches 2 -dropout 0.1  -batch_size 2048 -batch_type tokens -normalization tokens  -accum_count 2  -optim adam -adam_beta2 0.998 -decay_method noam -warmup_steps 8000 -learning_rate 2   -max_grad_norm 0 -param_init 0  -param_init_glorot -label_smoothing 0.1 -valid_steps 10000 -save_checkpoint_steps 10000 -tensorboard  -world_size 4 -gpu_ranks 0 1 2 3 -master_port 10001 -train_from /root/workspace/OpenNMT-py/toolkit/model_v6-2_enzh2_step_90000.pt

###4. filter long sentence(edit the script /root/workspace/OpenNMT/toolkit/filter_long_tk.py)
    python /root/workspace/OpenNMT/toolkit/filter_long_tk.py

###4. evaluate model
    python3 /root/workspace/OpenNMT-py/translate.py \
    -gpu 0 \
    -model /root/workspace/OpenNMT-py/toolkit/model_v6-2_enzh2_step_200000.pt \
    -src /root/workspace/translate_data/my_corpus_v6.en.tok.processed7-bpe-v6-2-filter3.test \
    -tgt /root/workspace/translate_data/my_corpus_v6.zh-cut.processed7-bpe-v6-2-filter3.test \
    -replace_unk -verbose \
    -output /root/workspace/OpenNMT-py/my-shell/model.v6-2_enzh2-20w.test.pred.atok

###5. calc BLEU
    perl /root/workspace/OpenNMT-py/tools/multi-bleu.perl /root/workspace/translate_data/my_corpus_v6.zh-cut.processed7-bpe-v6-2-filter3.test < /root/workspace/OpenNMT-py/my-shell/model.v6-2_enzh2-20w.test.pred.atok


## step 3 -  deploy server
    # start enzh server
    python3 /root/workspace/OpenNMT-py/my_server_enzh.py -gpu 6 -model /root/workspace/OpenNMT-py/my-shell/model_v6-2_enzh_step_170000.pt -verbose -src xxx
    # start zhen server
    python3 /root/workspace/OpenNMT-py/my_server_zhen.py ...
