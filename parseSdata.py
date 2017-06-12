import signal
import sys
import json
import jsonrpclib
import makesets
import pickle
from random import randint
from ILPformat import parse_json

OUT=None

class StanfordNLP:
    def __init__(self, port_number=8080):
        self.server = jsonrpclib.Server("http://localhost:%d" % port_number)

    def parse(self, text):
        return json.loads(self.server.parse(text))

nlp = StanfordNLP()

def cleannum(n):
    return ''.join([x for x in n if x.isdigit() or x=='.' or x=='x' or x=='x*'])


def make_eq(q,a,VERBOSE,TRAIN):
    bigtexamples = {x:([],[]) for x in ["+","*",'/','-','=']}
    
    wps = q #q is the questions
    
    
    for k in range(len(wps)):
        if VERBOSE:
            for i in range(len(wps)):
                print(i,wps[i])
            k = int(input())
        
        print(k)
        problem = wps[k]
        #print problem
        
        #First preprocessing, tokenize slightly
        problem = problem.strip().split(" ")
        for i,x in enumerate(problem):
            if len(x)==0: continue
            if x[-1] in [',','.','?']:
                problem[i] = x[:-1]+" "+x[-1]
        problem = ' '.join(problem)
        problem = " " + problem + " "
        
        #Percentage Putting
        Res = problem
        problem=""
        for i in range(len(Res)):
            if Res[i]=='%':
                problem += " percent"
            else:
                problem += Res[i]
        
        ##Change Percentage to times
        
        problem = problem.strip().split(" ")
        for i in range(len(problem)-1):
            if (problem[i+1]=='percent') or (problem[i+1]=='percentage') or (problem[i+1]=='Percentage') or (problem[i+1]=='Percent'):
                strval = problem[i]
                val=''
                if strval[0]=='$':
                    val=strval[1:]
                    val=float(val)/100.0
                    problem[i]=str(val)
                elif strval[0] in ['0','1','2','3','4','5','6','7','8','9']:
                    val=strval
                    val=float(val)/100.0
                    problem[i]=str(val)
                problem[i+1]='times'
        
        problem = ' '.join(problem)
        problem = " " + problem + " "
        
        print(problem)

        story = nlp.parse(problem)
        #print story['sentences']
        '''
        Gets the That returns a dictionary containing the keys sentences and coref. The key sentences contains a list of dictionaries for each sentence, which
        contain parsetree, text, tuples containing the dependencies, and words, containing information about parts of speech, recognized named-entities, etc:
        '''
        #print story
        pickle.dump(story,open("s_data/"+str(k)+".pickle",'wb'))
        continue

'''
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
'''


if __name__=="__main__":
    
    #q, a = sys.argv[1:3]
    
    inp = sys.argv[1] # Takes the problemSet name
    
    #q,a,e = parse_inp(inp)
    
    q,a = parse_json(inp) #A method imported from ILPformat.py and makes question -> q and solution -> a
    
    #print q
    #print a
    
    VERBOSE=False
    TRAIN=False
    '''
    if len(sys.argv)>3:
        if sys.argv[3]=='v':
            VERBOSE=True
        elif sys.argv[3]=='t':
            TRAIN = True
            OUT = sys.argv[4]
    '''
    make_eq(q,a,VERBOSE,TRAIN)


