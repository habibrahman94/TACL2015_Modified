import sys, os, pickle

d = pickle.load(open(sys.argv[1],'rb'))
named = {'+':'plus','-':'minus','/':'divide','*':'multiply','=':'equal'}
outf = sys.argv[1].split(".training")[0]+".data"
outl = sys.argv[1].split(".training")[0]+"_label.data"
f = open(outf,'w')
fL = open(outl,'w')

for k,x in enumerate(['+','-','*','/']):
#for k,x in enumerate(['+','-']):
#for k,x in enumerate(['*','/']):
    '''
    if k < 2:
        k=0
    else:
        k=1
    '''
    #k = int(k>1)
    #print("Formatting Training Data: "+str(len(d[x][0])))
    for v in d[x][0]:
        #print(v);input()
        fL.write(str(k)+"\n")
        for i,j in enumerate(v):
            f.write(str(j)+" ")
        f.write("\n")
    	print(len(v))

f.close()
fL.close()
