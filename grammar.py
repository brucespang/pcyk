import pickle
from collections import defaultdict
from nltk import tree, treetransforms
from nltk.corpus import treebank
from math import log

def trees():
    for f in treebank.fileids():
        for t in treebank.parsed_sents(f):
            t = tree.Tree(str(t))
            t.collapse_unary(collapsePOS=True)
            t.chomsky_normal_form()
            yield t

def count_tree(t, grammar):
    if len(t) == 2:
        grammar[t.node][(t[0].node, t[1].node)] += 1
        count_tree(t[0], grammar)
        count_tree(t[1], grammar)
    elif len(t) == 1:
        if isinstance(t[0], str):
            grammar[t.node][t[0]] += 1
        else:
            count_tree(t[0], grammar)
    else:
        print "unexpected len: " + len(t)
        raise
    
def normalize_grammar(grammar):
    normalized = {}
    for nt, productions in grammar.iteritems():
        total = float(sum(productions.values()))
        normalized[nt] = {nt:log(float(x)/total) for nt, x in productions.iteritems()}
    return normalized

def train_grammar(trees):
    grammar = defaultdict(lambda: defaultdict(int))
    sentence_tags = set()
    c = 0
    for tree in trees:
        c += 1
        if c > 100: break
        sentence_tags.add(tree.node)
        count_tree(tree, grammar)
    return (normalize_grammar(grammar), sentence_tags)

grammar = train_grammar(trees())
pickle.dump(grammar, open("grammar.pickle", 'w'))
