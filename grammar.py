import pickle
from collections import defaultdict
from nltk import tree, treetransforms
from nltk.corpus import treebank
from math import log

SMOOTHING_PARAMETER = 2

def trees():
    for f in treebank.fileids():
        for t in treebank.parsed_sents(f):
            t.chomsky_normal_form(horzMarkov=1)
            t.collapse_unary(collapsePOS=True)
            yield t

def count_tree(t, grammar):
    if len(t) == 1:
        if isinstance(t[0], str):
            grammar[t.node][t[0]] += 1
        else:
            count_tree(t[0], grammar)
    else:
        children = tuple([c.node for c in t])
        grammar[t.node][children] += 1
        for child in t:
            count_tree(child, grammar)
    
def normalize_grammar(grammar):
    normalized = {}
    for nt, productions in grammar.iteritems():
        total = float(sum(productions.values()))
        size = log(total + SMOOTHING_PARAMETER*len(productions))
        normalized[nt] = {}
        for lhs, count in productions.items():
            normalized[nt][lhs] = log(count) - size
    return normalized

def train_grammar(trees):
    grammar = defaultdict(lambda: defaultdict(int))
    sentence_tags = set()
    for tree in trees:
        sentence_tags.add(tree.node)
        count_tree(tree, grammar)
    return (normalize_grammar(grammar), sentence_tags)

grammar = train_grammar(list(trees())[0:3800])
print len(grammar[0])
# pickle.dump(grammar, open("grammar.pickle", 'w'))


