from html.parser import HTMLParser
from nltk.stem import PorterStemmer
import json
import pandas as pd
import re
import shelve

def _df_from_dict(dictObj:dict, toInt = False):
    df = pd.DataFrame.from_dict(dictObj, orient='index')
    df.fillna(0, inplace=True)
    if toInt: df = df.astype('int32')
    return df.transpose()

#Cite: https://stackoverflow.com/questions/47545052/convert-dataframe-rows-to-python-set
def _dict_from_df(df) -> dict:
    df = df.transpose()
    series_set = df.apply(frozenset, axis=1)
    new_df = series_set.apply(lambda a: set(a))
    return dict(new_df)

def _join_df_col(df1,df2):
    df3 = df1.merge(df2)
    df3.fillna(0, inplace=True)
    return df3.astype('int32')

class WeightFlags:
    def __init__(self) -> None:
        self._norm = 'normal'
        self._setFields = set()
        self._fields = {
            'title': 4,
            'header': 3,'h1': 3,'h2': 3,'b': 3,'strong': 3,'em': 3,
            'h3': 2,'h4': 2,'h5': 2,'h6': 2,'i': 2
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
    
    #Write inverted index to multiple shelve files
    def write(self, filePath:str = 'Shelve', count:int = 1) -> None:

        #Write pos index to file using Pos{count} as key
        # with shelve.open(f'{filePath}/index', 'c') as shelf:
        #     shelf[f'index{count}'] = self.getAllPos()
        #     shelf[f'weight{count}'] = self.getAllFields()

        termDict = {}
        for term in self._positions:
            docList = list(self._positions[term])
            dfCount = len(self._positions[term])
            tDict = {'df':dfCount, 'wTf':{}, 'docIds':list()}
            for docId in self._positions[term]:
                tDict['wTf'].update({docId:len(self._positions[term][docId]) + self._wFlag.getSum(self._weights[term][docId])})
            tDict['docIds'] = docList
            termDict[term] = json.dumps(tDict)
        
        with open(f'{filePath}/Posting{count}.txt', "w") as fp:
            for term in termDict:
                fp.write(f'{term}-{termDict[term]}\n')


    def load(self, words:list, filePath:str = 'Shelve', count:int = 1):
        with shelve.open(f'{filePath}/index', 'c') as shelf:
            # self._positions = shelf[f'index{count}']
            tempShelve = None
            for i in range(1,count+1):
                tempShelve = shelf[f'index{i}']
                for word in words:
                    if word in tempShelve:
                        if word in self._positions:
                            self._positions[word].update(tempShelve[word])
                        else:
                            self._positions[word] = tempShelve[word]
    
    def loadAll(self, filePath:str = 'Shelve', count:int = 10):
        with shelve.open(f'{filePath}/index', 'c') as shelf:
            for i in range(1,count+1):
                shelveDict = shelf[f'index{i}']
                if i == 1:
                    self._positions.update(shelveDict)
                else:
                    for term in shelveDict:
                        if term in self._positions:
                            self._positions[term].update(shelveDict[term])
                        else:
                            self._positions[term] = shelveDict[term]

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
        self._pos = 1
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

                    self._pos += 1

    def clear(self):
        self._pos = 1
        self._weights.clearFields()
    
    def getDocLen(self):
        return self._pos
    