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
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.multiclass import OneVsOneClassifier
from sklearn.multiclass import OneVsRestClassifier
from sklearn import decomposition

modelLocal = None
modelGlob = None
Lb = None
Gb = None
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
        Cmp = int(equations[k])
        #print(equations[k])
        #print(problem)
        if len(answers)==0:
            print("0 Answers \n"+str(equations[k])+" INCORRECT")
            if Cmp<=278:
                wrong += 1
            continue


        #make story
        story = read_parse(int(equations[k]))
        #sets = makesets.makesets(story['sentences'])
        sets = read_sets(int(equations[k]))
        i = 0

        for x in sets:
            x[1].details()

        xidx = [i for i,x in enumerate(sets) if x[1].num=='x']
        if not xidx:
            print(str(equations[k])+" INCORRECT NO X WHY")
            if Cmp<=278:
                wrong += 1
            continue

        xidx = xidx[0]
        
        #print k
        numlist = [(cleannum(v.num),v) for m,v in sets]
        numlist = [x for x in numlist if x[0]!='']
        allnumbs = {str(m):v for m,v in numlist}
        objs = {m:(0,v) for m,v in numlist}
        #print(objs.items())
        consts = [x for x in answers[0][1].split(" ") if x not in ['(',')','+','-','/','*','=',]]
        present = [x for x in consts if x in objs]
        if consts!=present:
            print(present,consts)
            print(str(equations[k])+" INCORRECT missing thing")
            if Cmp<=278:
                wrong += 1
            continue
        if len([x for x in objs if x not in consts])>0:
            print(str(equations[k])+" INCORRECT missing thing")
            if Cmp<=278:
                wrong +=1
            continue
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
            #score has the Local Model Score
            #gscore is the Global Model Score
            #Gb = 1.0 - Lb
            #proposed_score = (Lb*score+Gb*gscore)
            score *= gscore
            scores.append((score,j,eq,guess))
        scores = sorted(scores,reverse=True)
        righties = [x for x in scores if x[1]==1]
        #print(scores[:3])
        if not righties:
            if Cmp<=278:
                wrong+=1
            print("TOP SCORING NO CORRECT SOLUTION ,"+str(equations[k])+" INCORRECT")
            continue
        else:
            corr = righties[0][3]


        if len(scores)>0:
            if scores[0][1]==1: # Right if 1
                if Cmp<=278:
                    right += 1
                #print k
                #print equations[k]
                print(str(equations[k])+" CORRECT")
            else:
                if Cmp<=278:
                    wrong += 1
                print(str(equations[k])+" INCORRECT")
        else:
            if Cmp<=278:
                wrong += 1
            print(str(equations[k])+" INCORRECT")

    return (right,wrong)


def compute(p,op,e,target,problem,story,order,score=None,cons=None):
    if op == '=':
        vec = [order,score,cons]
        vec.extend(makesets.vector(p,e,problem,story,target))
        vec = [vec]
        #pca = decomposition.PCA(n_components=45)
        #pca.fit(vec)
        #vec = pca.transform(vec)
        #vec = vec.tolist()
        op_val = modelGlobal.predict_proba(vec)
        
    else:
        vec = makesets.vector(p,e,problem,story,target)
        vec = [vec]
        #pca = decomposition.PCA(n_components=45)
        #pca.fit(vec)
        #vec = pca.transform(vec)
        #vec = vec.tolist()
        op_val = modelLocal.predict_proba(vec)
    
    print op_val[0]
    
    op_val=op_val[0]
    if op == '+':
        val = op_val[0]
    if op == '-':
        val = op_val[1]
    if op == '*':
        val = op_val[2]
    if op == '/':
        val = op_val[3]
    if op == '=':
        val = op_val[1]
    
    
    c = makesets.combine(p[1],e[1],op)
    return (val,c,op_val)

def norm(Features, Label):
    Data = []
    for i in open(Features,'r'):
        Feat = []
        st = i.split(" ")
        for j in st:
            if j!="\n":
                Feat.append(float(j))
        Data.append(Feat)
    Lab = []
    for i in open(Label, 'r'):
        Lab.append(float(i))
    
    RetData = np.zeros((len(Data), len(Data[0])), dtype = np.float)
    RetLab = np.zeros(len(Lab), dtype = np.float)
    
    
    for i,item in enumerate(Data):
        Feat = np.zeros(len(item), dtype = np.float)
        Tm = item
        for j, it in enumerate(Tm):
            Feat[j]=it
        RetData[i]=Feat
    for i,item in enumerate(Lab):
        RetLab[i]=Lab[i]
    
    return (RetData, RetLab)



if __name__=="__main__":
    inp, Lfile, LLabelFile, gfile, gLabelFile= sys.argv[1:6]
    
    Lb = float(0.1 * float(sys.argv[6]))
    
    Local_Features, Local_Label = norm(Lfile, LLabelFile)
    Global_Features, Global_Label = norm(gfile, gLabelFile)
    
    '''
    PCA 
    #pca = decomposition.PCA(n_components=45)
    #pca.fit(Local_Features)
    #Local_Features = pca.transform(Local_Features)
    #Local_Features = Local_Features.tolist()
    
    #pca2 = decomposition.PCA(n_components=45)
    #pca2.fit(Global_Features)
    #Global_Features = pca2.transform(Global_Features)
    #Global_Features = Global_Features.tolist()
    
    '''
    
    modelLocal = OneVsRestClassifier(RandomForestClassifier())
    modelGlobal = OneVsRestClassifier(RandomForestClassifier())
    
    modelLocal.fit(Local_Features, Local_Label)
    modelGlobal.fit(Global_Features, Global_Label)
    
    inp = sys.argv[1]
    makesets.FOLD = sys.argv[1][-1]
    q,a,e = parse_inp(inp)
    right, wrong = make_eq(q,a,e)
    print(right,wrong,right/len(q))

