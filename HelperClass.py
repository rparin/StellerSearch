from collections import defaultdict
from html.parser import HTMLParser
from nltk.stem import PorterStemmer
import pandas as pd
import re

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

#Posting is an object that holds the term and info about that term for multiple documents
class Token:
    def __init__(self, tok:str) -> None:
        self._tok:str = tok
        self._positions = defaultdict(lambda: set())
        self._weights = defaultdict(lambda: dict)

    def addPosition(self, docId: int, pos:int):
        self._positions[docId].add(pos)
    
    def addWeight(self, docId:int, field:str, pos:int):
        if docId in self._weights:
            if field in self._weights[docId]:
                self._weights[docId][field].add(pos)
            else:
                self._weights[docId][field] = {pos}
        else:
            self._weights[docId] = {field:{pos}}

    #Getter functions
    def getToken(self) -> str:
        return self._tok
    
    def getAllPos(self) -> dict:
        return dict(self._positions)
    
    def getAllFields(self) -> dict:
        return dict(self._weights)
    
    def __getitem__(self, postType:str) -> dict:
        assert postType == 'pos' or postType == 'field', f"Token info '{postType}' does NOT exist!"
        
        if postType == 'pos':
            return self._positions
        
        if postType == 'field':
            return self._weights
    
    #Setters
    def addToken(self, token) -> None:
        self._positions.update(token.getAllPos())
        self._weights.update(token.getAllFields())
    
    #Overload print function to print obj info
    def __repr__(self) -> str:
        rStr = f'Token: {self._tok}'
        for docId in self._positions:
            rStr += f'\n\tDocId: {docId}, Freq: {len(self._positions[docId])}\n\t\tPos: {self._positions[docId]}\n\t\tWeights: {dict(self._weights[docId])}'
        return rStr
    
    def write(self, filePath:str = 'DevHDF5') -> None:
        fPath = filePath+'/Pos.hdf5'
        store = pd.HDFStore(fPath,mode='a')
        inStore = self._tok in store
        store.close()

        #Token already in file
        if inStore:
            oldDf = pd.read_hdf(fPath, self._tok, mode='r')
            oldDict = _dict_from_df(oldDf)
            self._positions.update(oldDict)

        #Convert Token pos to df
        df = _df_from_dict(self.getAllPos())
        df.to_hdf(fPath, key=self._tok)
    
#InvertedIndex is an object to hold multiple document objects
class InvertedIndex:
    def __init__(self) -> None:
        self._index = defaultdict(lambda: dict)

    #Setter functions
    def addToken(self, token:Token) -> None:
        if token.getToken() in self._index:
            self._index[token.getToken()].addToken(token)
        else:
            self._index[token.getToken()] = token

    #Getter functions
    def getTokenAmount(self) -> int:
        return len(self._index)
    
    #Overload in operator 
    #Example: if token:str in InvertedIndexObj
    def __contains__(self, token:str) -> bool:
        return token in self._index

    #Overload bracket operator to allow accessing inverted index doc and posting obj
    #Example: InvertedIndexObj[token:str]
    def __getitem__(self, tok):
        assert tok in self._index, f"Token '{tok}' does NOT exist!"
        return self._index[tok]

    #Overload print function to print obj info
    def __repr__(self) -> str:
        rStr = f'Total Tokens: {self.getTokenAmount()}\n'
        for token in self._index:
            rStr += f'{self._index[token]}\n\n'
        return rStr
    
    #Write inverted index to multiple shelve files
    def write(self, filePath:str = 'DevHDF5', count:int = 1) -> None:
        #Write Terms
        # for token in self._index:
        #     self._index[token].write(filePath)

        #Create Index pos dict
        posIndex = defaultdict(lambda: dict)
        wIndex = defaultdict(lambda: dict)
        for token in self._index:
            posIndex[token] = self._index[token].getAllPos()
            wIndex[token] = self._index[token].getAllFields()

        #Write pos index to file using Pos{count} as key
        df = _df_from_dict(dict(posIndex))
        df.to_hdf(f'{filePath}/Index.hdf5', key='pos'+str(count))

        #Write field index to file using fields{count} as key
        df = _df_from_dict(dict(wIndex))
        df.to_hdf(f'{filePath}/Index.hdf5', key='field'+str(count))

    #Clear inverted index
    def clear(self):
        self._index.clear()
    
class WeightFlags:
    def __init__(self) -> None:
        #Field not defined is considered normal weight
        self._fields = {'title', 'header', 'footer',
                       'h1','h2','h3','h4','h5','h6',
                       's', #strikethrough
                       'strike', #strikethrough
                       'i', #italic
                       'b','strong','em','a','article',
                       'caption','nav','menu','cite'}
        self._setFields = set()
    
    #Getters
    def isWeight(self,field:str) -> bool:
        return field in self._fields;

    def getActiveFields(self) -> set():
        if len(self._setFields) == 0:
            return {'normal'}
        return self._setFields

    #Setters
    def setField(self, field:str) -> None:
        self._setFields.add(field)

    def removeField(self, field:str) -> None:
        if field in self._setFields:
            self._setFields.remove(field)

    def clearFields(self) -> None:
        self._setFields.clear()

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

                    #create token if not in index
                    if token not in self._invIndex:
                        tempToken = Token(token)
                        self._invIndex.addToken(tempToken)

                    #Add Position for given docId
                    self._invIndex[token].addPosition(self._docId, self._pos)
                    
                    #Add Weight
                    for field in self._weights.getActiveFields():
                        self._invIndex[token].addWeight(self._docId, field, self._pos)

                    self._pos += 1

    def clear(self):
        self._pos = 1
        self._weights.clearFields()
    