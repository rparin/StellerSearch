from html.parser import HTMLParser
from nltk.stem import PorterStemmer
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
    
#InvertedIndex is an object to hold term posting information
class InvertedIndex:
    def __init__(self) -> None:
        self._positions = {}
        self._weights = {}

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
                rStr += f'\n\tDocId: {docId}, Freq: {len(self.getAllPos()[token][docId])}\n\t\t \
                Pos: {self.getAllPos()[token][docId]}'
                #rStr += '\n\t\tWeights: {self.getAllFields()[token][docId]}'
        return rStr
    
    #Write inverted index to multiple shelve files
    def write(self, filePath:str = 'Shelve', count:int = 1) -> None:

        #Write pos index to file using Pos{count} as key
        with shelve.open(f'{filePath}/index', 'c') as shelf:
            shelf[f'index{count}'] = self.getAllPos()

        #Write pos index to file using Pos{count} as key
        # df = _df_from_dict(self.getAllPos())
        # df.to_hdf(f'{filePath}/Index.hdf5', key='pos'+str(count))

        #Write field index to file using fields{count} as key
        # df = _df_from_dict(self.getAllFields())
        # df.to_hdf(f'{filePath}/Index.hdf5', key='field'+str(count))

    def load(self, words:list, filePath:str = 'Shelve', count:int = 1):
        with shelve.open(f'{filePath}/index', 'c') as shelf:
            # self._positions = shelf[f'index{count}']
            for i in range(1,count+1):
                for word in words:
                    self._positions[word] = shelf[f'index{i}'][word]

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

                    #Add Position for given docId
                    self._invIndex.addPosition(token, self._docId, self._pos)
                    
                    #Add Weight
                    for field in self._weights.getActiveFields():
                        self._invIndex.addWeight(token, self._docId, field, self._pos)

                    self._pos += 1

    def clear(self):
        self._pos = 1
        self._weights.clearFields()
    