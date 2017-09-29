python train_local_LR.py data/train$1;
python formattrainingdata_LR.py data/$1\.local.training;
python train_global_LR.py data/train$1 data/$1\.local.data data/$1\.local_label.data;
python inference_LR.py data/test$1 data/$1\.local.data data/$1\.local_label.data data/$1\.global.data data/$1\.global_label.data $2 | tee results/fold$1\.txt ;

