import signal
import sys
import json
import jsonrpclib
import makesets
import pickle
from random import randint
from train_local_elm import get_k_eqs
from train_local_elm import read_parse
from train_local_elm import read_sets
from train_local_elm import parse_inp
from functools import reduce
import numpy as np
import elm
#sys.path.insert(0, 'libsvm/python')
#from svmutil import *

elmLocal = None
elmGlob = None

class StanfordNLP:
    def __init__(self, port_number=8080):
        self.server = jsonrpclib.Server("http://localhost:%d" % port_number)

    def parse(self, text):
        return json.loads(self.server.parse(text))

nlp = StanfordNLP()

def cleannum(n):
    n = ''.join([x for x in n if x.isdigit() or x=='.' or x=='x' or x=='x*'])
    return n
multi = None
glob = None

def make_eq(q,a,equations):
    wps = q #open(q).readlines()
    answs = a #open(a).readlines()
    right = 0
    wrong = 0
    
    #print(len(wps))
    for k in range(len(wps)):
        #print(k)
        answers = get_k_eqs(equations[k],g=True,a=True)
        seeneq = []
        seen = []
        for x in answers:
            if x[1] not in seeneq:
                seen.append(x)
                seeneq.append(x[1])
        answers = seen
        answers = list(set(answers))
        


        #First preprocessing, tokenize slightly
        problem = wps[k]#.lower()
        problem = problem.strip().split(" ")
        for i,x in enumerate(problem):
            if len(x)==0:continue
            if x[-1] in [',','.','?']:
                problem[i] = x[:-1]+" "+x[-1]
        problem = ' '.join(problem)
        problem = " " + problem + " "
        #print(equations[k])
        #print(problem)
        if len(answers)==0:print("0 Answers \n"+str(equations[k])+" INCORRECT"); wrong += 1; continue


        #make story
        story = read_parse(int(equations[k]))
        #sets = makesets.makesets(story['sentences'])
        sets = read_sets(int(equations[k]))
        i = 0

        for x in sets:
            x[1].details()

        xidx = [i for i,x in enumerate(sets) if x[1].num=='x']
        if not xidx:
            print(str(equations[k])+" INCORRECT NO X WHY");wrong += 1; continue

        xidx = xidx[0]
        
        #print k
        numlist = [(cleannum(v.num),v) for m,v in sets]
        numlist = [x for x in numlist if x[0]!='']
        allnumbs = {str(m):v for m,v in numlist}
        objs = {m:(0,v) for m,v in numlist}
        #print(objs.items())
        consts = [x for x in answers[0][1].split(" ") if x not in ['(',')','+','-','/','*','=',]]
        present = [x for x in consts if x in objs]
        if consts!=present: print(present,consts);print(str(equations[k])+" INCORRECT missing thing");wrong += 1; continue
        if len([x for x in objs if x not in consts])>0: print(str(equations[k])+" INCORRECT missing thing");wrong +=1;continue
        scores = []


        for j,eq,cons,guess in answers:
            consts = [x for x in eq.split(" ") if x not in ['(',')','+','-','/','*','=',]]
            order = int(consts==[x[0] for x in numlist])
            if order == 0: continue
            #j = randint(0,len(answers)-1)
            #eq = answers[j]
            trips = []
            #print(j,eq)
            l,r = [x.strip().split(' ') for x in eq.split('=')]
            consts = " ".join([x for x in answers[0][1].split(" ") if x not in ['(',')','+','-','/','*',]])
            consts = consts.split(" = ")
            sp = (objs[consts[0].split(" ")[-1]],objs[consts[1].split(" ")[0]])
             
            target = 'x'
            target = (target,objs[target])

            #find innermost parens?
            #print(eq)
            sides = []
            thisscore = []
            for i,compound in enumerate([l,r]):
                while len(compound)>1:
                    if "(" in compound:
                        rpidx = (len(compound) - 1) - compound[::-1].index('(')
                        lpidx = rpidx+compound[rpidx:].index(")")
                        subeq = compound[rpidx+1:lpidx]
                        substr = "("+''.join(subeq)+")"
                        compound = compound[:rpidx]+[substr]+compound[lpidx+1:]
                    else:
                        subeq = compound[0:3]
                        substr = "("+''.join(subeq)+")"
                        compound = [substr]+compound[3:]
                    p,op,e = subeq
                    p = objs[p]
                    e = objs[e]
                    op = op.strip()
                    pute = compute(p,op,e,target,problem,story,order,thisscore, cons)
                    objs[substr]=pute
                    if pute == -1:
                        exit()
                    score,c,vals = pute
                    thisscore.append(score)
                    #print(subeq,score)
                sides.append(objs[compound[0]])
            p = sides[0]; e = sides[1]
            score = 1
            for s in thisscore: score *= s
            gscore = compute(p,'=',e,target,problem,story,order,score,cons)[0]
            #print("gscore ",gscore)
            score *= gscore
            scores.append((score,j,eq,guess))
        scores = sorted(scores,reverse=True)
        righties = [x for x in scores if x[1]==1]
        #print(scores[:3])
        if not righties:
            wrong+=1
            print("TOP SCORING NO CORRECT SOLUTION ,"+str(equations[k])+" INCORRECT")
            continue
        else:
            corr = righties[0][3]


        if len(scores)>0:
            if scores[0][1]==1: # Right if 1
                right += 1
                #print k
                #print equations[k]
                print(str(equations[k])+" CORRECT")
            else:
                wrong += 1
                print(str(equations[k])+" INCORRECT")
        else:
            wrong += 1
            print(str(equations[k])+" INCORRECT")

    return (right,wrong)


def compute(p,op,e,target,problem,story,order,score=None,cons=None):
    if op == '=':
        vec = [order,score,cons]
        vec.extend(makesets.vector(p,e,problem,story,target))
        
        file_to_work = open('data/tm.data', 'w')
        file_to_work.write(repr(0))
        for i in range(len(vec)):
            file_to_work.write(" "+repr(vec[i]))
        file_to_work.write(" \n")
        file_to_work.write(repr(0))
        for i in range(len(vec)):
            file_to_work.write(" "+repr(vec[i]))
        file_to_work.write(" \n")
        file_to_work.close()
        
        test_data = elm.read('data/tm.data')
        
        #op_label, op_acc, op_val = svm_predict([-1], [vec], glob ,'-q -b 1')
        te_result = elmGlob.test(test_data)
        te_result.predicted_targets = np.round(te_result.predicted_targets)
        ret = te_result.predicted_targets[0]
        if ret<0.0:
            val = -1
        else:
            val = 1
    else:
        vec = makesets.vector(p,e,problem,story,target)
        file_to_work = open('data/tm.data', 'w')
        file_to_work.write(repr(0))
        for i in range(len(vec)):
            file_to_work.write(" "+repr(vec[i]))
        file_to_work.write(" \n")
        file_to_work.write(repr(0))
        for i in range(len(vec)):
            file_to_work.write(" "+repr(vec[i]))
        file_to_work.write(" \n")
        file_to_work.close()
        
        test_data = elm.read('data/tm.data')
        #op_label, op_acc, op_val = svm_predict([-1], [vec], multi ,'-q -b 1')
        te_result = elmLocal.test(test_data)
        te_result.predicted_targets = np.round(te_result.predicted_targets)
        val = te_result.predicted_targets[0] #Round Modified
    
    op_val=[]
    
    c = makesets.combine(p[1],e[1],op)
    return (val,c,op_val)


if __name__=="__main__":
    inp, mfile, gfile = sys.argv[1:4]
    multi = elm.read(mfile)
    glob = elm.read(gfile)
    ###
    elmLocal = elm.ELMKernel()
    elmGlob = elm.ELMKernel()
    
    tr_res_local = elmLocal.train(multi)
    tr_res_glob = elmGlob.train(glob)
    
    #q, a = sys.argv[1:3]
    inp = sys.argv[1]
    makesets.FOLD = sys.argv[1][-1]
    q,a,e = parse_inp(inp)
    right, wrong = make_eq(q,a,e)
    print(right,wrong,right/len(q))

