from collections import defaultdict
from html.parser import HTMLParser
import re


#Posting is an object to hold token information for a single document
class Posting:
    def __init__(self, docId:int) -> None:
        self._docId:int = docId
        self._positions = set()
        self._weights = defaultdict(lambda: set())

    #Setters functions
    def addPosition(self, pos:int) -> None:
        self._positions.add(pos)

    def addWeight(self, wType:str, pos:int) -> None:
        self._weights[wType].add(pos)

    #Getter functions
    def getDocId(self) -> int:
        return self._docId

    def getFreq(self) -> int:
        return len(self._positions)
    
    def printWeights(self, getStr = False) -> None | str:
        rStr = f'\t\tWeights:'
        if len(self._weights) == 0:
            rStr += 'None\n'
        else:
            for w in self._weights:
                rStr += f'\n\t\t\t{w}:{self._weights[w]}'
        if getStr: return rStr
        print(rStr)

    #Overload bracket operator to allow access of positions or weights
    #Example: postingObj['positions'] or postingObj['wt']
    def __getitem__(self, key):
        if key == 'positions' or key == 'pos': return self._positions
        if key == 'weights' or key == 'wt': return self._weights
        assert key, f"{key} does NOT exist!"
        

    #Overload print function to print obj info
    def __repr__(self) -> str:
        rStr = f'\tDocId: {self._docId}, Freq: {self.getFreq()}\n\t\tPositions:'
        if self.getFreq() == 0:
            rStr += ' None'
        else:
            rStr += f' {self._positions}'
        
        rStr += f'\n{self.printWeights(getStr=True)}'
        return rStr
    
#Token is an object to hold a string, its total freq across all doc's and multiple Posting objects
class Token:
    def __init__(self, tok:str) -> None:
        self._tok:str = tok
        self._totalFreq:int = 0
        self._postings = defaultdict(lambda: dict)
    
    def addPosting(self, posting: Posting):
        self._postings[posting.getDocId()] = posting
        self._totalFreq += posting.getFreq()

    #Getter functions
    def getToken(self) -> str:
        return self._tok

    def getPosting(self, docId:int) -> Posting:
        return self._postings[docId]
    
    #Overload in operator 
    #Example: if docId:int in TokenObj
    #Check if token contains docId posting
    def __contains__(self, docId:int) -> bool:
        return docId in self._postings
    
    def getTf(self) -> int:
        return self._totalFreq
    
    def recountTf(self) -> int:
        self._totalFreq:int = 0
        for docId in self._postings:
            self._totalFreq += self._postings[docId].getFreq()
        return self.getTf()
    
    #Overload bracket operator to allow accessing inverted index doc and posting obj
    #Example: TokenObj[docId:int]
    def __getitem__(self, docId:int) -> Posting:
        assert docId in self._postings, f"Document #{docId} does NOT exist!"
        return self._postings[docId]
    
    #Overload print function to print obj info
    def __repr__(self) -> str:
        rStr = f'Token: {self._tok}, Total Freq: {self.getTf()}\n'
        for docId in self._postings:
            rStr += f'{self._postings[docId]}\n'
        return rStr

    
#InvertedIndex is an object to hold multiple document objects
class InvertedIndex:
    def __init__(self) -> None:
        self._index = defaultdict(lambda: dict)

    #Setter functions
    def addToken(self, token:Token) -> None:
        self._index[token.getToken()] = token

    def reCountTf(self) -> int:
        for token in self._index:
            self._index[token].recountTf()

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
            rStr += f'{self._index[token]}\n'
        return rStr
    
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

    def handle_starttag(self, tag, attrs):
        if self._weights.isWeight(tag):
            self._weights.setField(tag)

    def handle_endtag(self, tag):
        if self._weights.isWeight(tag):
            self._weights.removeField(tag)

    def handle_data(self, data):
        line = data.strip()
        if line != '':
            for token in re.split('[^a-z0-9]', line.lower()):
                if (token != ''):

                    #create token, add posting using given docId
                    if token not in self._invIndex:
                        tempPost = Posting(self._docId)
                        tempToken = Token(token)
                        tempToken.addPosting(tempPost)
                        self._invIndex.addToken(tempToken)

                    #Token exists but posting for document does not exist
                    else:
                        if self._docId not in self._invIndex[token]:
                            tempPost = Posting(self._docId)
                            self._invIndex[token].addPosting(tempPost)

                    #Update posting for given docId
                    #Add Position
                    self._invIndex[token][self._docId].addPosition(self._pos)
                    
                    #Add Weight
                    for field in self._weights.getActiveFields():
                        self._invIndex[token][self._docId].addWeight(field,self._pos)

                    self._pos += 1

    def clear(self):
        self._pos = 1
        self._weights.clearFields()