##Code for "Parsing Algebraic Word Problems into Equations"

`Rik Koncel-Kedziorski, Hannaneh Hajishirzi, Ashish Sabharwal, Oren Etzioni, Siena Dumas Ang`

##TACL 2015 vol 3



SingleEQ Dataset is in questions.json
Replace this with a similarly formatted dataset as desired


*Running Instructions:

Download, install, and run corenlp-python https://pypi.python.org/pypi/corenlp-python
Please read the instructions for the CPLEX code at https://gitlab.cs.washington.edu/ALGES/TACL2015/tree/master/arith-ilp/arith-cplex
For those without access to CPLEX libraries, a statically linked executable is available

*Run the following sequence of commands:

[code]
./preSplit.sh questions.json

python3 split_data.py questions.json

for i in {0..4}; do python3 fold_train_test.py $i questions.json ; done

cp data/questions.jsonILP.input arith-ilp/arith-cplex/scripts

cd !$

./revisedSplitQuestions.sh questions.jsonILP.input ILP.out

./runall.sh ILP.out

mv ILP.out ../../../

cd !$

for i in {0..4}; do ./runone.sh $i ; done
[\code]


```Results are placed in results folder```


