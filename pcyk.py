import sys
import pickle
from random import choice
from collections import defaultdict
from nltk.corpus import treebank

# The grammar
# A line like:
#    NP = [['Det', 'N'], ['N'], ['N', 'PP'], 
# means
#    NP -> Det N
#    NP -> N
#    NP -> N PP
# grammar = Dict(
#         S = {('NPD','VP'): 0.5, ('NPDs', 'VPs'): 0.5},
#         NPD = {('Det', 'NP'):1},
#         NP = {('NP', 'PP'):0.25, ('J', 'NP'):0.25, 'man':0.1, 'dog':0.1, 'pickle':0.1, 'ball':0.1, 'light':0.1},
#         NPDs = {('Dets', 'NPs'):1},
#         NPs = {('NPs', 'PP'):0.25, ('J', 'NPs'):0.25, 'men':0.1, 'dogs':0.1, 'pickles':0.1, 'balls':0.1, 'lights':0.1},
#         VP = {('V', 'NPDs'):0.33, ('V', 'NPD'):0.33, ('V', 'PP'):0.34},
#         V = {'pickles':0.1, 'sees': 0.1, 'likes': 0.1, 'liked': 0.1, 'lights': 0.1, 'sleeps': 0.1, 'slept': 0.1, 'hits': 0.1, 'hit': 0.1, 'dances': 0.1},
#         VPs = {('Vs', 'NPDs'):0.33, ('Vs', 'NPD'):0.33, ('Vs', 'PP'):0.34},
#         Vs = {'pickle': 0.1, 'see': 0.1, 'like': 0.1, 'liked': 0.1, 'light': 0.1, 'sleep': 0.1, 'slept': 0.1, 'hit': 0.1, 'dance': 0.1, 'danced': 0.1},
# 	PP = {('P', 'NPs'):0.33, ('P', 'NPD'):0.33, ('P', 'NPDs'):0.34},
#         Det = {'the':0.5, 'a':0.5},
#         Dets = {'the':0.5, 'some':0.5},
# 	P = {'with':1},
# 	J = {'red':0.33, 'big':0.33, 'light':0.34},
#         )

def sentences():
    for f in treebank.fileids():
        for t in treebank.sents(f):
            yield ' '.join(t)

def generate(phrase):
    "Generate a random sentence or phrase"
    if isinstance(phrase, dict): 
        return map(generate, phrase)
    elif phrase in grammar:
        return [phrase] + generate(choice(grammar[phrase]))
    else: return [phrase]
    
def flatten_tree(tree):
    if isinstance(tree, list):
        if len(tree) > 2:
            return flatten_tree(tree[1]) + ' ' + flatten_tree(tree[2])
        else:
            return flatten_tree(tree[1])
    else:
        return tree

def mappend(fn, list):
    "Append the results of calling fn on each element of list."
    return reduce(lambda x,y: x+y, map(fn, list))

def producers(constituent, grammar):
    "Argument is a list containing the rhs of some rule; return all possible lhs's"
    results = {}
    for (lhs,rhss) in grammar.items():
	for rhs,p in rhss.iteritems():
	    if rhs == constituent:
		results[lhs] = p
    return results

def parse(s, grammar, sentence_tags):
    "The CYK parser.  Returns the set of possible parse trees for sentence"
    sentence = s.split()
    length = len(sentence)
    trees = [[defaultdict(lambda: {}) for i in range(length+1)] for j in range(length)]
            
    # Fill the diagonal of the table with the parts-of-speech of the words
    for k in range(1,length+1):
        for producer,p in producers(sentence[k-1], grammar).iteritems():
            trees[k-1][k][producer].append([producer, p, sentence[k-1]])

    nonproducers = defaultdict(lambda: {})
    for nt,rs in grammar.iteritems():
        for r,p in rs.iteritems():
            if isinstance(r, tuple):
                nonproducers[nt][r] = p

    for width in range(2,len(sentence)+1):
        for start in range(len(sentence)-width+1):
            end = start + width
            for span in range(start, end):
                for nt,rs in nonproducers.iteritems():
                    for r,p in rs.iteritems():
                        for p1 in trees[start][span][r[0]]:
                            for p2 in trees[span][end][r[1]]:
                                prob = p+p1[1]+p2[1]
                                trees[start][end][nt].append([nt, prob, p1, p2])
                                
    for t in sentence_tags:
        for parse in trees[0][len(sentence)][t]:
            yield parse

def format(tree, level=0):
    if isinstance(tree, list):
        s = "[%s:%.5f"%(format(tree[0]), tree[1])
        for i in range(2, len(tree)):
            s += "\n" + " "*2*level + format(tree[i], level+1)
        s += "]"
        return s
    else:
        return tree

def print_language(size):
    "Randomly generate sentences, saving and printing the unique ones"
    language = set()
    while len(language) < size:
        s = generate('S')
	language.add(flatten_tree(s))
        
    for s in language:
        # parses = parse(s, grammar)
	print s
        # for p in range(len(parses)):
        #     print "  " + str(p+1) + ". " + format(parses[p], 4)

def test_parser():
    for _ in range(100):
        s = generate('S')
        f = flatten_tree(s)
        if s not in parse(f, grammar):
            print "[ERROR] " + format(f)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print >> sys.stderr, "Usage: %s grammar.pickle"%(sys.argv[0])
        exit(1)

    (grammar,sentence_tags) = pickle.load(open(sys.argv[1]))

    for s in sentences():
        print s
        for p in parse(s, grammar, sentence_tags):
            print format(p)

