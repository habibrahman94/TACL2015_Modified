# Code to convert the list of entities into an output file

def main(sets, index,answ,fn):
    entities = [x[1] for x in sets ]
    getOutputValues(entities, index,answ,fn)

def getTempEntities():
    entities = []
    entities.append(EntityTemp('seashell', '70'))
    entities.append(EntityTemp('seashell', 'x'))
    entities.append(EntityTemp('seashell', '27'))
    return entities

def getOutputValues(entities, index,answ,fn):
    constants = []
    types = []

    for e in entities:
        # constants
        constants.append(e.num)
        types.append('"'+e.entity+'"')

    printOutputValues(constants, types, index,answ,fn)

def printOutputValues(constants, types, index,answ,fn):
    file = open('data/'+fn+'ILP.input', 'a')
    file.write('\n'+str(index)+'\n')
    file.write('quantities :')
    writeVals(file, constants)
    file.write('\n' + 'types :')
    writeVals(file, types)
    file.write('\n' + 'operators : + - * / =')
    file.write('\n' + 'n : ' + str((len(constants) * 2 - 1)))
    file.write('\nanswer : ' + str(answ))
    file.write('\n')

def writeVals(file, values):
    for v in values:
        file.write(' ' + str(v))


if __name__ == "__main__":
    main()
