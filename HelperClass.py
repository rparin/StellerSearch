from html.parser import HTMLParser
from nltk.stem import PorterStemmer
from heapq import heapify, heappush, heappop
import numpy as np
from numpy.linalg import norm
import json
import math
import re
import pyarrow.feather as feather

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
    def isWeight(self,field:str) -> bool:
        return field in self._fields;

    def getActiveFields(self) -> set():
        if len(self._setFields) == 0:
            return {self._norm}
        return self._setFields
    
    def getSum(self, weightDict:dict) -> int:
        sumFields = 0
        for field in weightDict:
            if field != self._norm:
                sumFields += (self._fields[field] * len(weightDict[field]))
        return sumFields

    #Setters
    def setField(self, field:str) -> None:
        self._setFields.add(field)

    def removeField(self, field:str) -> None:
        if field in self._setFields:
            self._setFields.remove(field)

    def clearFields(self) -> None:
        self._setFields.clear()
    
#InvertedIndex is an object to hold term posting information
class InvertedIndex:
    def __init__(self) -> None:
        self._positions = {}
        self._weights = {}
        self._wFlag = WeightFlags()

    def addPosition(self, term:str, docId: int, pos:int):
        if term in self._positions:
            if docId in self._positions[term]:
                self._positions[term][docId].add(pos)
            else:
                self._positions[term].update({docId: {pos}})
        else:
            self._positions[term] = {docId:{pos}}
            
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
    def getTokenAmount(self) -> int:
        return len(self._positions)
    
    def getAllPos(self) -> dict:
        return self._positions
    
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
    def write(self, filePath:str = 'Shelve', count:int = 1) -> None:
        termDict = {}
        termList = []
        for term in self._positions:
            dfCount = len(self._positions[term])
            tDict = {'df':dfCount, 'wTf':{}}
            for docId in self._positions[term]:
                tDict['wTf'].update({docId:len(self._positions[term][docId]) + self._wFlag.getSum(self._weights[term][docId])})
            termDict[term] = json.dumps(tDict)
            termList.append(term)
            
        termList.sort()
        with open(f'{filePath}/Posting{count}.txt', "w") as fp:
            for term in termList:
                fp.write(f'{term}-{termDict[term]}\n')

    #Clear inverted index
    def clear(self):
        self._positions.clear()
        self._weights.clear()
        self._wFlag.clearFields()

class HTMLTokenizer(HTMLParser):
    def __init__(self, docId:int, invIndex:InvertedIndex, convert_charrefs: bool = True) -> None:
        super().__init__(convert_charrefs=convert_charrefs)
        self._docId = docId
        self._invIndex = invIndex
        self._weights = WeightFlags()
        self._pos = 0
        self._weightVal = 0
        self.stemmer = PorterStemmer()

    def handle_starttag(self, tag, attrs):
        if self._weights.isWeight(tag):
            self._weights.setField(tag)

    def handle_endtag(self, tag):
        if self._weights.isWeight(tag):
            self._weights.removeField(tag)

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
                        self._weightVal += self._weights._fields[field]

                    self._pos += 1

    def clear(self):
        self._pos = 0
        self._weightVal = 0
        self._weights.clearFields()
    
    def getDocLen(self):
        return self._pos + self._weightVal
    
class QueryParser:
    def __init__(self, indexFp, docIdFp, indexFile, docFile) -> None:
        self._termFpDf = self._getFpDataframe(indexFp)
        self._docFpDf = self._getFpDataframe(docIdFp)
        self._indexFile = indexFile
        self._docFile = docFile
        self._queryCount = None
        self._queryDict = None
        self._queryOrder = None
        self._docIds = None

    def runQuery(self, queryStr:str, ignore:set = set()) -> list:
        self.setQuery(queryStr)
        if self._queryCount['len'] == 1:
            self._docIds = self._getCList()
            return self.getCosRank(ignore=ignore)
        else:
            self._docIds = self._getDocIds()
        return self.getTf_IdfRank(ignore=ignore)

    def setQuery(self, queryStr) -> None:
        self._queryCount:dict = {'terms':{}, 'len': 0}
        self._queryDict, self._queryOrder = self._stemQuery(queryStr)
        
    def getTf_IdfRank(self,  amt = 10, sort = True, ignore:set = set()) -> list[tuple]:
        docRanks = []; heapify(docRanks)
        tfSet = set()
        for docIdStr in self._docIds:
            if docIdStr not in ignore:
                sumTf_Idf = 0
                for term in self._queryDict:
                    sumTf_Idf += self._queryDict[term][docIdStr]
                sumTf_Idf = round(sumTf_Idf, 5)
                if sumTf_Idf not in tfSet:
                    if len(docRanks) < amt:
                        heappush(docRanks, (sumTf_Idf,docIdStr))
                        tfSet.add(sumTf_Idf)
                    else:
                        if sumTf_Idf > docRanks[0][0]:
                            heappop(docRanks)
                            heappush(docRanks, (sumTf_Idf,docIdStr))
                            tfSet.add(sumTf_Idf)
        if sort: docRanks.sort(reverse=True)
        return docRanks
    
    def printTf_IdfRank(self) -> None:
        docRanks = self.getTf_IdfRank()
        for tup in docRanks:
            url = self._getDocData(int(tup[1]))['url']
            print(tup[1], url, tup[0])

    def getCosRank(self, amt = 10, ignore:set = set()) -> list:
        tfIdf_doc_amt = min(len(self._docIds), 15)
        docRanks = self.getTf_IdfRank(tfIdf_doc_amt, False, ignore=ignore)
        queryVec = self._getQVector()
        coRanks = []; heapify(coRanks)
        for tup in docRanks:
            docIdStr = tup[1]
            docVec = self._getDocVector(docIdStr)
            coSim = round(self._calc_cos_sim(queryVec, docVec),5)
            resTup = (coSim, docIdStr)
            if len(coRanks) < amt:
                heappush(coRanks, resTup)
            else:
                if coSim > coRanks[0][0]:
                    heappop(coRanks)
                    heappush(coRanks, resTup)
        coRanks.sort(reverse=True)
        return coRanks
    
    def printCosRank(self) -> None:
        cosRank = self.getCosRank()
        for tup in cosRank:
            url = self._getDocData(int(tup[1]))['url']
            print(tup[1], url, tup[0])

    def _getQVector(self) -> list:
        qVector = []
        for tup in self._queryOrder:
            term = tup[1]
            idf = self._queryDict[term]['idf']
            tfIdf = self._calculate_tf_idf(self._queryCount['terms'][term],idf)
            qVector.append(tfIdf)
        return qVector
    
    def _getDocVector(self, docIdStr:str) -> list:
        docVector = []
        for tup in self._queryOrder:
            term = tup[1]
            tfIdf = self._getTermData(term)[docIdStr]
            docVector.append(tfIdf)
        return docVector

    def _calculate_tf_idf(self,tf, idf):
        return ((1 + math.log(tf)) * idf)
    
    def _calc_cos_sim(self, A:list, B:list) -> float:
        return np.dot(A,B)/(norm(A)*norm(B))

    def _getFpDataframe(self, file):
        fpDf = feather.read_feather(file)
        return fpDf

    def _getTermData(self, term:str):
        return self._getData(self._indexFile, self._termFpDf, term)
    
    def _getDocData(self, docId:int):
        return self._getData(self._docFile, self._docFpDf, docId)
        
    def _getData(self, file, fp:dict, value:str) -> dict:
        dataInfo = None
        if value not in fp['fp']: return dataInfo
        file.seek(fp['fp'][value])
        tInfo = file.readline().strip().split('>')[1]
        return json.loads(tInfo) 
    
    def _stemQuery(self, queryStr:str) -> dict:
        stemmer = PorterStemmer()
        queryDict = {}
        intersectOrder = []; heapify(intersectOrder)
        line = queryStr.strip()
        if line != '':
            for aToken in re.split('[^a-z0-9]', line.lower()):
                if (aToken != ''):
                    token = stemmer.stem(aToken)
                    if token not in queryDict:
                        termData = self._getTermData(token)
                        if termData:
                            queryDict[token] = termData
                            heappush(intersectOrder, (termData['idf']*-1,token))
                            self._queryCount['terms'][token] = 1
                            self._queryCount['len'] += 1
                    else:
                        self._queryCount['terms'][token] += 1
                        self._queryCount['len'] += 1
        return queryDict, intersectOrder
    
    def _getDocIds(self) -> set:
        intersection_keys = None
        for tup in self._queryOrder:
            term = tup[1]
            if intersection_keys == None:
                intersection_keys = set(self._queryDict[term].keys())
                intersection_keys.remove('cList')
                intersection_keys.remove('idf')
            else:
                intersection_keys = intersection_keys & self._queryDict[term].keys()

        return intersection_keys
    
    def _getCList(self) -> set:
        cList_Intersection = None
        for tup in self._queryOrder:
            term = tup[1]
            if cList_Intersection == None:
                cList_Intersection = set(self._queryDict[term]['cList'])
            else:
                cList_Intersection = cList_Intersection & set(self._queryDict[term]['cList'])

        return cList_Intersection