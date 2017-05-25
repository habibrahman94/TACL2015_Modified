import sys
import makesets
import pickle
from random import randint

def read_parse(k):
    return pickle.load(open('s_data/'+str(int(k))+'.pickle', 'rb'))

def read_sets(k):
    return pickle.load(open('madesets/'+str(int(k))+'.pickle','rb'))

def cleannum(n):
    n = ''.join([x for x in n if x.isdigit() or x=='.' or x=='x' or x=='x*'])
    return n

def training(trips,problem,story,target):
    #this function take the trips and creates positive and negative training instances from them
    
    texamples = {x:([],[]) for x in ["+","*",'/','-','=']}
    for op,a,b in trips:
        if op == '=':
            vec = makesets.eqvector(a,b,problem,story,target)
        else:
            vec = makesets.vector(a,b,problem,story,target)
        texamples[op][0].append(vec)

    return texamples


def make_eq(q,a,equations):
    bigtexamples = {x:([],[]) for x in ["+","*",'/','-','=']}
    wps = q #open(q).readlines()
    answs = a #open(a).readlines()

    for k in range(len(wps)):

        #First preprocessing, tokenize slightly
        problem = wps[k]#.lower()
        problem = problem.strip().split(" ")
        for i,x in enumerate(problem):
            if len(x)==0:continue
            if x[-1] in [',','.','?']:
                problem[i] = x[:-1]+" "+x[-1]
        problem = ' '.join(problem)
        problem = " " + problem + " "
        print(k)
        print(problem)

        #story = nlp.parse(problem)
        story = read_parse(int(equations[k]))
        eqs = get_k_eqs(equations[k])
        answers = [x[1] for x in eqs if x[0]==1]
        if answers == []: continue
        answers = list(set(answers))
        print(answers)


        #make story
        #story = nlp.parse(problem)
        #sets = makesets.makesets(story['sentences'])
        sets = read_sets(equations[k])
        i = 0

        xidx = [i for i,x in enumerate(sets) if x[1].num=='x']
        if not xidx:
            print("NO X WHY");continue


        numlist = [(cleannum(v.num),v) for k,v in sets]
        numlist = [x for x in numlist if x[0]!='']
        allnumbs = {str(k):v for k,v in numlist}
        objs = {k:(0,v) for k,v in numlist}
        print(objs.items())
        consts = [x for x in answers[0].split(" ") if x not in ['(',')','+','-','/','*','=',]]
        present = [x for x in consts if x in objs]
        if present!=consts: 
            print(present,consts);print("missing thing");#continue
            continue

        oanswers = []
        for eq in answers:
            consts = [x for x in eq.split(" ") if x not in ['(',')','+','-','/','*','=',]]
            order = int(consts==[x[0] for x in numlist])
            if order == 0:continue
            else: oanswers.append(eq)
        if oanswers == []: continue

        answers = oanswers
        print(answers)
            
        
        simpleanswers = [x for x in answers if x.split(" ")[-2]=="="]
        if simpleanswers:
            answers = simpleanswers
        else: answers = [answers[randint(0,len(answers)-1)]]
        print(answers)
        #simpleanswers = []
        
        for j,eq in enumerate(answers):
            trips = []
            print(j,eq)
            l,r = [x.strip().split(' ') for x in eq.split('=')]
            
            target = 'x'
            target = (target,objs[target])

            #find innermost parens?
            sides = []
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
                    if True:
                        p,op,e = subeq
                        p = objs[p]
                        e = objs[e]
                        op = op.strip()
                        trips.append((op,p,e))
                        pute = (0,makesets.combine(p[1],e[1],op))
                        objs[substr]=pute
                    if pute == -1:
                        exit()
            t = training(trips,problem,story,target)
            for op in t:
                bigtexamples[op][0].extend(t[op][0])
                bigtexamples[op][1].extend(t[op][1])
    pickle.dump(bigtexamples,open('data/'+sys.argv[1][-1]+".local.training",'wb'))



def parse_inp(inp):
    q=[]
    a=[]
    e=[]
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

def get_k_eqs(i,k=100,g=False,a=False):
    digit = "{0:0=3d}".format(int(i))
    exprs = []
    with open(eqsdir+"/q"+digit+".txt.out") as f:
        f = f.readlines()[3:-1]
        j = 0
        while j<k:
            if j>=len(f): break
            line = f[j]
            line = line.split(" | ")
            good = line[0].split(": ")[1]
            exp = line[6]
            for s in ['(',')','+','-','*','/','=']:
                exp = exp.replace(s,' '+s+' ')
            exp = exp.replace('  ',' ').strip()
            if g:
                cons = int(line[3])
                if cons == 0:
                    cons = 1
                else:
                    cons = 1/(cons+1)
                if a:
                    answ = line[5]
                    exprs.append((int(good),exp,cons,answ))
                else:
                    exprs.append((int(good),exp,cons))

            else:
                exprs.append((int(good),exp))
            j+=1
    return exprs

eqsdir = "ILP.out"


if __name__=="__main__":
    #q, a = sys.argv[1:3]
    inp = sys.argv[1]
    #eqsdir = sys.argv[2]
    makesets.FOLD = sys.argv[1][-1]
    q,a,e = parse_inp(inp)

    make_eq(q,a,e)


