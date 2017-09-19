import nltk
folder = nltk.data.find("/home/habib/nltk_data")
corpusReader = nltk.corpus.PlaintextCorpusReader(folder, '.*\.txt')

print "The number of sentences =", len(corpusReader.sents())
print "The number of patagraphs =", len(corpusReader.paras())
print "The number of words =", len([word for sentence in corpusReader.sents() for word in sentence])
print "The number of characters =", len([char for sentence in corpusReader.sents() for word in sentence for char in word])
