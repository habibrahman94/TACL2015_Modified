echo 'File Romoving Started...'

rm -rf ILP.out

rm -rf data/*.local.m
rm -rf data/*.local.training
rm -rf data/*.local.data
rm -rf data/test*
rm -rf data/train*
rm -rf data/*input
rm -rf data/*txt

rm -rf madesets/*
rm -rf s_data/*
rm -rf arith-ilp/arith-cplex/scripts/*.input

echo 'File Romoving Ended...'
