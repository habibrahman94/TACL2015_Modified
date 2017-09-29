#!/bin/bash

## Author: Habibur Rahman, CSE, RUET, Bangladesh, May 2017


if [ $# -ne 1 ]; then
  echo "USAGE: ./TACL2015_ELM.sh problemSet"
  exit 1
fi

problemSet=$1

echo "Problem Set Name: "$problemSet


echo '################################################################################'
echo './preSplit.sh $problemSet'
./preSplit.sh $problemSet

echo '################################################################################'
echo 'python split_data.py $problemSet'
python split_data.py $problemSet

echo '################################################################################'
echo 'for i in {0..4}; do python fold_train_test.py $i $problemSet ; done'
for i in {0..4}; do python fold_train_test.py $i $problemSet ; done


path=$problemSet'ILP.input'

echo '################################################################################'
echo 'cp data/$path arith-ilp/arith-cplex/scripts'
cp data/$path arith-ilp/arith-cplex/scripts

echo '################################################################################'
echo 'cd arith-ilp/arith-cplex/scripts'
cd arith-ilp/arith-cplex/scripts

echo '################################################################################'
echo './revisedSplitQuestions.sh $path ILP.out'
./revisedSplitQuestions.sh $path ILP.out

#Check the nSols variable in the runall.sh file for Number of Solutions
echo '################################################################################'
echo './runall.sh ILP.out'
./runall.sh ILP.out

echo '################################################################################'
echo 'mv ILP.out ../../../'
mv ILP.out ../../../

echo '################################################################################'
echo 'cd ../../../'
cd ../../../

echo '################################################################################'
echo 'for i in {0..4}; do ./runone.sh $i ; done'
for i in {0..4}; do ./runone_LR.sh $i ; done

#echo '################################################################################'
#echo 'File Romoving Started...'

#rm -rf ILP.out

#rm -rf data/*.local.m
#rm -rf data/*.local.training
#rm -rf data/*.local.data
#rm -rf data/test*
#rm -rf data/train*
#rm -rf data/*input
#rm -rf data/*txt

#rm -rf madesets/*
#rm -rf s_data/*
#rm -rf arith-ilp/arith-cplex/scripts/*.input

#echo 'Removing Completed!'

##to remove the folder with all its contents(including all interior folders):
##rm -rf /path/to/directory
##to remove all the contents of the folder(including all interior folders) but not the folder itself:
##rm -rf /path/to/directory/*
##to remove all the "files" from inside a folder(not removing interior folders):
##rm -f /path/to/directory/*



##########################################
##Running runone_LR.sh with Multiple Lb, Gb Values as my Equation
#for j in {0..11}; do for i in {0..4}; do ./runone_LR.sh $i $j; done && cd results && python FileReader.py && cd ..; done

