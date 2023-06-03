from html.parser import HTMLParser
from nltk.stem import PorterStemmer
from heapq import heapify, heappush, heappop
import numpy as np
from numpy.linalg import norm
import json
import math
import re
import pyarrow.feather as feather

#This class is a dictionary that defines how much weight a given tag has
class WeightFlags:
    def __init__(self) -> None:
        self._norm = 'normal'
        self._setFields = set()
        self._fields = {
            'title': 100,
            'header': 80,'h1': 80,'h2': 80,'b': 80,'strong': 80,'em': 80,
            'h3': 50,'h4': 50,'h5': 50,'h6': 50,'i': 50,
            self._norm: 0
        }
    
    #Getters

    #Check if a field is a weight
    def isWeight(self,field:str) -> bool:
        return field in self._fields;

    #Get all weights for a given Term
    def getActiveFields(self) -> set():
        if len(self._setFields) == 0:
            return {self._norm}
        return self._setFields
    
    #Calculate the sum of all the weights for a given term
    def getSum(self, weightDict:dict) -> int:
        sumFields = 0
        for field in weightDict:
            if field != self._norm:
                sumFields += (self._fields[field] * len(weightDict[field]))
        return sumFields

    #Setters

    #Add a weight to a term
    def setField(self, field:str) -> None:
        self._setFields.add(field)

    #Remove a weight from a term
    def removeField(self, field:str) -> None:
        if field in self._setFields:
            self._setFields.remove(field)

    #Clear all weights from a term
    def clearFields(self) -> None:
        self._setFields.clear()
    
#InvertedIndex is an object to hold term posting information
class InvertedIndex:
    def __init__(self) -> None:
        self._positions = {} #dict to hold {term:{docId:positions},..}
        self._weights = {} #dict to hold {term:{docId:weights},..}
        self._wFlag = WeightFlags() #Object to calculate sum of weights for a given term

    #Store term position to inverted index
    def addPosition(self, term:str, docId: int, pos:int):
        if term in self._positions:
            if docId in self._positions[term]:
                self._positions[term][docId].add(pos)
            else:
                self._positions[term].update({docId: {pos}})
        else:
            self._positions[term] = {docId:{pos}}
    
    #Store term weight to inverted index
    def addWeight(self, term:str, docId:int, field:str, pos:int):
        if term in self._weights:
            if docId in self._weights[term]:
                if field in self._weights[term][docId]:
                    self._weights[term][docId][field].add(pos)
                else:
                    self._weights[term][docId][field] = {pos}
            else:
                self._weights[term].update({docId:{field:{pos}}})
        else:
            self._weights[term] = {docId:{field:{pos}}}
        
    #Getter functions

    #Calculate how many tokens currently in Inverted Index
    def getTokenAmount(self) -> int:
        return len(self._positions)
    
    #Return all the positions stored for all terms
    def getAllPos(self) -> dict:
        return self._positions
    
    #Return all the positions stored for all terms weights
    def getAllFields(self) -> dict:
        return self._weights
    
    #Overload in operator 
    #Example: if token:str in InvertedIndexObj
    def __contains__(self, token:str) -> bool:
        return token in self._positions

    #Overload bracket operator to allow accessing inverted index doc and posting obj
    #Example: InvertedIndexObj[token:str]
    def __getitem__(self, postType:str):
        assert postType == 'pos' or postType == 'field', f"Token info '{postType}' does NOT exist!"
        
        if postType == 'pos':
            return self._positions
        
        if postType == 'field':
            return self._weights

    #Overload print function to print obj info
    def __repr__(self) -> str:
        rStr = f'Total Tokens: {self.getTokenAmount()}'
        for token in self.getAllPos():
            rStr += f'\nToken: {token}'
            for docId in self.getAllPos()[token]:
                rStr += f'\n\tDocId: {docId}, Freq: {len(self.getAllPos()[token][docId])} \
                \n\t\tPos: {self.getAllPos()[token][docId]}\n\t\tWeights: {self.getAllFields()[token][docId]}'
        return rStr
    
    #Write inverted index to multiple txt files
    def write(self, filePath:str = 'Data', count:int = 1) -> None:
        termDict = {} #Store posting info for each term
        termList = []

        #Go through all terms in Index and organize term data to write to file
        for term in self._positions:

            #Get doc freq count for each term and save it
            dfCount = len(self._positions[term])
            tDict = {'df':dfCount, 'wTf':{}} #Structure of posting info

            #Combine positions and weights for a term, weighted Term Freq (wTf)
            for docId in self._positions[term]:
                tDict['wTf'].update({docId:len(self._positions[term][docId]) + self._wFlag.getSum(self._weights[term][docId])})
            
            #Save term info to data structures
            termDict[term] = json.dumps(tDict)
            termList.append(term)

        #Write terms to file in abc order
        termList.sort()
        with open(f'{filePath}/Posting{count}.txt', "w") as fp:
            for term in termList:
                fp.write(f'{term}-{termDict[term]}\n')

    #Clear inverted index
    def clear(self):
        self._positions.clear()
        self._weights.clear()
        self._wFlag.clearFields()

#Class to tokenize html content and add tokens to inverted Index
class HTMLTokenizer(HTMLParser):
    def __init__(self, docId:int, invIndex:InvertedIndex, convert_charrefs: bool = True) -> None:
        super().__init__(convert_charrefs=convert_charrefs)
        self._docId = docId
        self._invIndex = invIndex
        self._weights = WeightFlags()
        self._pos = 0
        self._weightVal = 0
        self.stemmer = PorterStemmer()

    #Check if tag is a weight if so keep track of that weight
    def handle_starttag(self, tag, attrs):
        if self._weights.isWeight(tag):
            self._weights.setField(tag)

    #Remove weight from term
    def handle_endtag(self, tag):
        if self._weights.isWeight(tag):
            self._weights.removeField(tag)

    #Parse the tokens in the html content
    #For each weight assign points to given terms
    def handle_data(self, data):
        line = data.strip()
        if line != '':
            for aToken in re.split('[^a-z0-9]', line.lower()):
                if (aToken != ''):
                    token = self.stemmer.stem(aToken)

                    #Add Position for given docId
                    self._invIndex.addPosition(token, self._docId, self._pos)
                    
                    #Add Weight
                    for field in self._weights.getActiveFields():
                        self._invIndex.addWeight(token, self._docId, field, self._pos)

                        #Keep track of weights separately from position
                        self._weightVal += self._weights._fields[field]

                    #Increment position
                    self._pos += 1

    #Clear html parser
    def clear(self):
        self._pos = 0
        self._weightVal = 0
        self._weights.clearFields()
    
    #return doc len which is the amount of tokens in a doc and offset weights calculated
    def getDocLen(self):
        return self._pos + self._weightVal
    
#This class gathers documents for a given query using cosine sim and tfIdf ranking
class QueryParser:
    #Pass in file pointers and File objects to query
    #File pointers are the index of index files
    #File objects are the index files
    def __init__(self, indexFp, docIdFp, indexFile, docFile) -> None:
        self._termFpDf = self._getFpDataframe(indexFp)
        self._docFpDf = self._getFpDataframe(docIdFp)
        self._indexFile = indexFile
        self._docFile = docFile
        self._queryCount = None
        self._queryDict = None
        self._queryOrder = None
        self._docIds = None

    #For a given query run, grab a set of documents for that query
    #For 1 word queries we use a champion list 
    # If the word has a low tfIdf we do not do cosine sim
    def runQuery(self, queryStr:str, ignore:set = set()) -> list:
        #Stem the query
        doCosSim = self.setQuery(queryStr)

        #Check if the query is valid
        if self._queryCount['len'] < 1: return []

        #Calculate whether to do a cosine sim (slow and accurate)
        # or a fast TfIdf Ranking
        if doCosSim: 
            self._docIds = self._getDocIds()
            return self.getCosRank(ignore=ignore)

        term = self._queryOrder[0][1]
        if self._queryCount['len'] == 1 and self._queryDict[term]['idf'] > 0.35:
            self._docIds = self._getCList()
            return self.getCosRank(ignore=ignore)
        else:
            self._docIds = self._getDocIds()
        return self.getTf_IdfRank(ignore=ignore)

    #Stem query and gather tfidf info for query
    def setQuery(self, queryStr) -> None:
        self._queryCount:dict = {'terms':{}, 'len': 0}
        toCosSim, self._queryOrder = self._stemQuery(queryStr)
        return toCosSim
        
    # Get top 10 TFIDf documents for a given query
    # Ignore set is an option to not rank documents in that set
    # Using priority set to get only 10 TfIdf ranked documents
        # Duplicate or similar scoring documents not counted
    def getTf_IdfRank(self,  amt = 10, sort = True, ignore:set = set()) -> list[tuple]:
        #Create priority set
        docRanks = []; heapify(docRanks)
        tfSet = set()
        
        #Go through and rank X documents
        # do not rank documents in ignore set
        for docIdStr in self._docIds:
            if docIdStr not in ignore:

                #Calculate the sum tfIdf for a given doc
                sumTf_Idf = 0
                for term in self._queryDict:
                    sumTf_Idf += self._queryDict[term][docIdStr]
                sumTf_Idf = round(sumTf_Idf, 5)

                #Add tfIdf to priority set if it is within the current top 10
                if sumTf_Idf not in tfSet:
                    if len(docRanks) < amt:
                        heappush(docRanks, (sumTf_Idf,docIdStr))
                        tfSet.add(sumTf_Idf)
                    else:
                        if sumTf_Idf > docRanks[0][0]:
                            heappop(docRanks)
                            heappush(docRanks, (sumTf_Idf,docIdStr))
                            tfSet.add(sumTf_Idf)

        #Sort the documents based on decreasing TfIdf Rank
        if sort: docRanks.sort(reverse=True)
        return docRanks
    
    #Calculate and print the top TfIdf document for the given query
    def printTf_IdfRank(self) -> None:
        docRanks = self.getTf_IdfRank()
        for tup in docRanks:
            url = self._getDocData(int(tup[1]))['url']
            print(tup[1], url, tup[0])


    # Get top 10 Cosine Sim documents for a given query
    # Ignore set is an option to not rank documents in that set
    # Using priority set to get only X amount TfIdf ranked documents
            # Duplicate or similar scoring documents not counted
        #Using X amount of TfIdf ranked documents choose Y amount of  
        #  documents based on high Cosine Sim score
    def getCosRank(self, amt = 10, ignore:set = set()) -> list:
        #Get X amount of TfIdf ranked documents
        tfIdf_doc_amt = min(len(self._docIds), 15)
        docRanks = self.getTf_IdfRank(tfIdf_doc_amt, False, ignore=ignore)

        #Calculate query vector, vector of query tfIdf
        queryVec = self._getQVector()

        #Create a heap to store top Y Cosine sim score documents
        coRanks = []; heapify(coRanks)

        for tup in docRanks:

            #Calculate cosine similarity between query and document
            docIdStr = tup[1]
            docVec = self._getDocVector(docIdStr)
            coSim = round(self._calc_cos_sim(queryVec, docVec),5)

            # Add document to heap if it is within the Top Y Cosine sim score documents
            resTup = (coSim, docIdStr)
            if len(coRanks) < amt:
                heappush(coRanks, resTup)
            else:
                if coSim > coRanks[0][0]:
                    heappop(coRanks)
                    heappush(coRanks, resTup)

        #Sort the documents based on decreasing Cosine Sim Score
        coRanks.sort(reverse=True)
        return coRanks
    
    #Calculate and print the top Cosine Sim documents for a given query
    def printCosRank(self) -> None:
        cosRank = self.getCosRank()
        for tup in cosRank:
            url = self._getDocData(int(tup[1]))['url']
            print(tup[1], url, tup[0])

    #Calculate the query vectors
    def _getQVector(self) -> list:
        qVector = []
        for tup in self._queryOrder:
            term = tup[1]
            idf = self._queryDict[term]['idf']
            tfIdf = self._calculate_tf_idf(self._queryCount['terms'][term],idf)
            qVector.append(tfIdf)
        return qVector
    
    #Calculate the doc vector
    #Order based on highest idf to lowest idf term
    def _getDocVector(self, docIdStr:str) -> list:
        docVector = []
        for tup in self._queryOrder:
            term = tup[1]
            tfIdf = self._getTermData(term)[docIdStr]
            docVector.append(tfIdf)
        return docVector

    #Given tf and idf caclulate tfIdf
    def _calculate_tf_idf(self,tf, idf):
        return ((1 + math.log10(tf)) * idf)
    
    #Given two vectors calculate the cosine similarity between them
    def _calc_cos_sim(self, A:list, B:list) -> float:
        return np.dot(A,B)/(norm(A)*norm(B))

    #Open and load the index of index file
    def _getFpDataframe(self, file):
        fpDf = feather.read_feather(file)
        return fpDf

    #Get term data which is a json dict of {'docId':tfIdf, 'idf': float}
    def _getTermData(self, term:str):
        return self._getData(self._indexFile, self._termFpDf, term)
    
    #Get doc data which is a json dict of {'docId':url, 'docLen': int}
    def _getDocData(self, docId:int):
        return self._getData(self._docFile, self._docFpDf, docId)

    #go to a given Index file position and return json dict    
    def _getData(self, file, fp:dict, value:str) -> dict:
        dataInfo = None
        if value not in fp['fp']: return dataInfo
        file.seek(fp['fp'][value])
        tInfo = file.readline().strip().split('>')[1]
        return json.loads(tInfo) 
    
    #Tokenize the query and get info about query
    # to calculate tfIdf and gets a set order to parse query
    def _stemQuery(self, queryStr:str) -> dict:
        stemmer = PorterStemmer() #Object to stem query term

        #Do a cosine similarity rank if terms have high idf
        doCosineSim = True

        #Hold query Data {'idf': float, 'docId': tfIdf}
        self._queryDict = {}

        #Store query order based on highest idf value
        intersectOrder = []; heapify(intersectOrder)

        #Tokenize the query
        line = queryStr.strip()
        if line != '':
            for aToken in re.split('[^a-z0-9]', line.lower()):
                if (aToken != ''):
                    #Stem a term
                    token = stemmer.stem(aToken)

                    #Check if term valid
                        #Store term if not already stored
                    if token not in self._queryDict:
                        termData = self._getTermData(token)
                        if termData:
                            self._queryDict[token] = termData

                            if termData['idf'] < 2.6:
                                doCosineSim = False

                            #Sort term based on decreasing idf value
                            heappush(intersectOrder, (termData['idf']*-1,token))
                            self._queryCount['terms'][token] = 1
                            self._queryCount['len'] += 1
                    else:
                        self._queryCount['terms'][token] += 1
                        self._queryCount['len'] += 1               
        return doCosineSim, intersectOrder
    
    # Get all documents where the query term(s) shows up
    def _getDocIds(self) -> set:
        intersection_keys = None

        # Go through the query based on highest idf first
        for tup in self._queryOrder:
            term = tup[1]

            if intersection_keys == None:
                #Create a set based on the first term
                intersection_keys = set(self._queryDict[term].keys())

                #Remove not needed keys
                intersection_keys.remove('cList')
                intersection_keys.remove('idf')
            else:
                #Keep intersecting set with next term set until complete
                intersection_keys = intersection_keys & self._queryDict[term].keys()

        return intersection_keys
    
    # Intersect the champion lists of query terms
    def _getCList(self) -> set:
        cList_Intersection = None

        # Go through the query based on highest idf first
        for tup in self._queryOrder:
            term = tup[1]
            if cList_Intersection == None:

                #Create a set based on the first term
                cList_Intersection = set(self._queryDict[term]['cList'])
            else:
                
                #Keep intersecting set with next term set until complete
                cList_Intersection = cList_Intersection & set(self._queryDict[term]['cList'])

        return cList_Intersection