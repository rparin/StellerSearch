from HelperClass import InvertedIndex
from nltk.stem import PorterStemmer
from collections import defaultdict
import math
import re
import shelve

def calculate_idf(N, df):
    idf = math.log((N + 0.1) / (df + 0.1))
    return idf

def getTfIdf(tf, df, N):
    return tf * calculate_idf(N, df)

def stemQuery(query:str) -> list:
    stemmer = PorterStemmer()
    queryList = list()
    line = query.strip()
    if line != '':
        for aToken in re.split('[^a-z0-9]', line.lower()):
            if (aToken != ''):
                token = stemmer.stem(aToken)
                queryList.append(token)
    return queryList

def getDfDict(query:set, invIndex):
    queryDict = defaultdict(lambda: '')
    for token in query:
        if token in invIndex:
            queryDict[token] = len(invIndex['pos'][token]) #df
        else:
            queryDict[token] = 0
    return queryDict

def getDocIds(qDict:dict, invIndex) -> set:
    unionSet = set()
    for word in qDict:
        if len(unionSet) == 0:
            unionSet = set(invIndex['pos'][word].keys())
        else:
            unionSet = unionSet.intersection(set(invIndex['pos'][word].keys()))
    return unionSet

def getTfIdfDict(qDict:dict, invIndex, N) -> dict:
    tfIdfDict = defaultdict(lambda: 0)
    for docId in getDocIds(qDict, invIndex):
        for word in qDict:
            tf = len(invIndex['pos'][word][docId])
            tfIdfDict[docId] += getTfIdf(tf, qDict[word], N)
    
    #Sort based on tfIdf
    return {k: v for k, v in sorted(tfIdfDict.items(), key=lambda item: item[1], reverse=True)}

def getTopResults(idDict, limit):
    count = 0
    for docId in idDict:
        with shelve.open(f'Shelve/docId', 'c') as shelf:
            print(shelf[str(docId)])
            count += 1
        if count >= limit: return

def main():
    N = 16258
    while True:
        query = input('> ')
        stemList = stemQuery(query)
        invIndex = InvertedIndex()
        invIndex.load(stemList,count=6)
        qDict = getDfDict(stemList,invIndex)
        tfIdfDict = getTfIdfDict(qDict, invIndex, N)
        getTopResults(tfIdfDict,5)

if __name__ == "__main__":
    main()