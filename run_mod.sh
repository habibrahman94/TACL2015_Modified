python train_local_elm.py data/train$1;
python formattrainingdata_elm.py data/$1\.local.training;
python train_global_elm.py data/train$1 data/$1\.local.data;
python inference_elm.py data/test$1 data/$1\.local.data data/$1\.global.data | tee results/fold$1\.txt ;

