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
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.multiclass import OneVsOneClassifier
from sklearn.multiclass import OneVsRestClassifier
from random import sample
import numpy as np
from sklearn import decomposition

modelNB = None
def pca_function(V):
    V[V==0] = -1
    V[V>0 ] = 1
    #print V
    v = []
    v.append(V)
    print len(v)
    pca = decomposition.PCA(n_components=45)
    pca.fit(v)
    v = pca.transform(v)
    print v
    return v

def compute(p,op,e,target,problem,story,order): # Returns the val of probability for the operator 'op'
    vec = makesets.vector(p,e,problem,story,target)
    vec = pca_function(vec)
    op_val = modelNB.predict_proba(vec)
    
    #print op_val[0]
    
    op_val=op_val[0]
    if op == '+':
        val = op_val[0]
    if op == '-':
        val = op_val[1]
    if op == '*':
        val = op_val[2]
    if op == '/':
        val = op_val[3]
    
    c = makesets.combine(p[1],e[1],op)
    return (val,c,op_val)


class StanfordNLP:
    def __init__(self, port_number=8080):
        self.server = jsonrpclib.Server("http://localhost:%d" % port_number)

    def parse(self, text):
        return json.loads(self.server.parse(text))

nlp = StanfordNLP()

def cleannum(n):
    n = ''.join([x for x in n if x.isdigit() or x=='.' or x=='x' or x=='x*'])
    return n

def kill(signum, frame):
    raise Exception("end of time")

def training(a,b,problem,story,target,j,order,score,constraints):
    #this function take the trips and creates positive and negative training instances from them
    
    #if j == 0:
    #    j=-1
    vec = [j,order,score,constraints]
    vec.extend(makesets.eqvector(a,b,problem,story,target))

    return vec


def make_eq(q,a,equations):
    tdata = []
    wps = q #open(q).readlines() #List of the Problem Text
    answs = a #open(a).readlines() # List of the Answers of the problem

    for k in range(len(wps)):
        print(k,equations[k])
        answers = get_k_eqs(equations[k],g=True) # Positive / Negative, Expr, and OBJ_SCORE
        #simpleanswers = [x for x in answers if x[1].split(" ")[-2] == '=']
        #if simpleanswers:
        #    answers = simpleanswers
        good = list(set([x for x in answers if x[0]==1])) # Positive Expresions
        bad = list(set([x for x in answers if x[0]==0]))[:len(good)] # Negative Expresions
        '''
        if len(bad)>len(good):
            bad = sample(bad,len(good))
        '''
        answers = good+bad
        if answers == []: continue
        answers = list(set(answers)) # Gets the distincts


        #First preprocessing, tokenize slightly
        problem = wps[k]#.lower()
        problem = problem.strip().split(" ")
        for i,x in enumerate(problem):
            if len(x)==0:continue
            if x[-1] in [',','.','?']:
                problem[i] = x[:-1]+" "+x[-1]
        problem = ' '.join(problem)
        problem = " " + problem + " "
        print(problem)

        #make story
        #story = nlp.parse(problem)
        story = read_parse(int(equations[k]))
        #sets = makesets.makesets(story['sentences'])
        sets = read_sets(int(equations[k]))
        i = 0

        xidx = [i for i,x in enumerate(sets) if x[1].num=='x']
        if not xidx:
            print("NO X WHY");continue

        #TODO look for 2 xes
        xidx = xidx[0]


        numlist = [(cleannum(v.num),v) for k,v in sets] #takes original Number or variables
        numlist = [x for x in numlist if x[0]!='']
        allnumbs = {str(i):v for i,v in numlist}
        objs = {i:(0,v) for i,v in numlist}
        #print(numlist)
        consts = [x for x in answers[0][1].split(" ") if x not in ['(',')','+','-','/','*','=',]]
        #print(consts)
        present = [x for x in consts if x in objs]
        if present!=consts: print(present,consts);print("missing thing");continue

        scores = []
        #print(answers)

        for j,eq,cons in answers: #j is Good or Bad , Eq is the Expr ...
            consts = [x for x in eq.split(" ") if x not in ['(',')','+','-','/','*','=',]]
            order = int(consts==[x[0] for x in numlist])
            #if order == 0:continue
            trips = []
            print(j,eq)
            l,r = [x.strip().split(' ') for x in eq.split('=')] #Divides the Expersion by left and Right
            consts = " ".join([x for x in answers[0][1].split(" ") if x not in ['(',')','+','-','/','*',]])
            consts = consts.split(" = ")
            
            target = 'x'
            target = (target,objs[target])

            #find innermost parens?
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
                    pute = compute(p,op,e,target,problem,story,order)
                    objs[substr]=pute
                    if pute == -1:
                        exit()
                    score,c,vals = pute
                    thisscore.append(score)
                sides.append(objs[compound[0]])
            p = sides[0]; e = sides[1]
            #thisscore.append(compute(p,'=',e,target,problem,story,order,sp)[0])
            score = 1
            for s in thisscore: score *= s
            #scores.append((score,j,eq))
            tdata.append(training(sides[0],sides[1],problem,story,target,j,order,score,cons))

    f = open("data/"+sys.argv[1][-1]+".global.data",'w')
    fL = open("data/"+sys.argv[1][-1]+".global_label.data",'w')
    for v in tdata:
        fL.write(str(v[0])+"\n")
        for i,j in enumerate(v[1:]):
            f.write(str(j)+" ")
        f.write("\n")
    

def parse_inp(inp):
    q=[] # List of The problem Texts
    a=[] # List of the Answers of the Problems
    e=[] # List of the Problem Numbers Actually, But used for equations
    with open(inp) as f:
        f = f.readlines()
        i=0
        while i<len(f):
            q.append(f[i])
            i+=1
            e.append(f[i])
            i+=1
            a.append(f[i])
            i+=1
    return (q,a,e)

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
    
    Local_Features, Local_Label = norm(sys.argv[2], sys.argv[3])
    
    #print Local_Features
    
    pca = decomposition.PCA(n_components=45)
    #print Local_Features
    pca.fit(Local_Features)
    Local_Features = pca.transform(Local_Features)
    Local_Features = Local_Features.tolist()
    
    
    modelNB = OneVsRestClassifier(RandomForestClassifier())
    modelNB.fit(Local_Features, Local_Label)
    #print modelNB.predict(Local_Features)
    #print len(Local_Features[0])
    
    inp = sys.argv[1] #train'$1'
    
    
    makesets.FOLD = sys.argv[1][-1]
    q,a,e = parse_inp(inp)
    make_eq(q,a,e)


