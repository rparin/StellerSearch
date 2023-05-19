from collections import defaultdict
from html.parser import HTMLParser
from nltk.stem import PorterStemmer
import shelve
import re

#Posting is an object that holds the term and info about that term for multiple documents
class Token:
    def __init__(self, tok:str) -> None:
        self._tok:str = tok
        self._positions = defaultdict(lambda: set())
        self._weights = defaultdict(lambda: dict)
        self._docId = set()

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
        
    def addDoc(self, docId:int):
        self._docId.add(docId)

    #Getter functions
    def getToken(self) -> str:
        return self._tok
    
    def getAllPos(self) -> dict:
        return dict(self._positions)
    
    def getAllDocId(self) -> set:
        return self._docId
    
    def getAllWeights(self) -> dict:
        return dict(self._weights)
    
    def __getitem__(self, postType:str) -> dict:
        assert postType == 'pos' or postType == 'field', f"Token info '{postType}' does NOT exist!"
        
        if postType == 'pos':
            return self._positions
        
        if postType == 'field':
            return self._weights
    
    #Setters
    def setWeights(self, weights:dict) -> None:
        self._weights = defaultdict(dict, weights)

    def setPos(self, pos:dict) -> None:
        self._positions = defaultdict(set, pos)

    def setAllDocId(self, docId:set) -> None:
        self._docId = docId
    
    #Overload print function to print obj info
    def __repr__(self) -> str:
        rStr = f'Token: {self._tok}'
        for docId in self.getAllDocId():
            rStr += f'\n\tDocId: {docId}, Freq: {len(self._positions[docId])}\n\t\tPos: {self._positions[docId]}\n\t\tWeights: {dict(self._weights[docId])}'
        return rStr
    
    def write(self, filePath:str = 'Shelve') -> None:
        pass
        # for docId in self._postings:
        #     postObj = self._postings[docId]
        #     token = self.getToken()

        #     #Store which document(s) token appears
        #     with shelve.open(f'{filePath}/Postings', 'c') as shelf:
        #         if token in shelf:
        #             shelf[token] += f',{docId}'
        #         else:
        #             shelf[token] = f'{docId}'

    
#InvertedIndex is an object to hold multiple document objects
class InvertedIndex:
    def __init__(self) -> None:
        self._index = defaultdict(lambda: dict)

    #Setter functions
    def addToken(self, token:Token) -> None:
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
    def write(self, filePath:str = 'Shelve') -> None:
        for token in self._index:
            self._index[token].write(filePath)

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
                        tempToken.addDoc(self._docId)
                        self._invIndex.addToken(tempToken)
                    else:
                        #Add docId to token if not already in there
                        if self._docId not in self._invIndex[token].getAllDocId():
                            self._invIndex[token].addDoc(self._docId)

                    #Add Position for given docId
                    self._invIndex[token].addPosition(self._docId, self._pos)
                    
                    #Add Weight
                    for field in self._weights.getActiveFields():
                        self._invIndex[token].addWeight(self._docId, field, self._pos)

                    self._pos += 1

    def clear(self):
        self._pos = 1
        self._weights.clearFields()
    