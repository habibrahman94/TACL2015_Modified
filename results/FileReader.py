# read a text file as a list of lines
# find the last line, change to a file you have
Right = 0.0
Wrong = 0.0
Total = 0.0
for i in range(5):
    File = 'fold'+repr(i)+'.txt'
    fileHandle = open ( File,"r" )
    lineList = fileHandle.readlines()
    fileHandle.close()
    LstLine = lineList[-1].replace(')', '')
    LstLine = LstLine.replace('(', '')
    LstLine = LstLine.split(',')
    for i in range(len(LstLine)):
        LstLine[i] = float(LstLine[i])
    Right+=LstLine[0]
    Wrong+=LstLine[1]
Total=Right+Wrong
Accuracy = (Right/Total)
Accuracy*=100.0
f = open("Result.txt", "a+")
f.write(repr(Accuracy)+'\n')
f.close()
print 'Accuracy: '+repr(Accuracy)
