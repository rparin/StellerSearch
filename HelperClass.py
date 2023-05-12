from collections import defaultdict
from html.parser import HTMLParser
import re

#Posting is an object to hold token information for a single document
class Posting:
    def __init__(self, tok:str) -> None:
        self._tok = tok
        self._positions = set()

    #Setters functions
    def addPosition(self, pos:int) -> None:
        self._positions.add(pos)

    #Getter functions
    def getToken(self) -> str:
        return self._tok

    #Overload bracket operator to allow access of positions and weights
    #Example: postingObj['positions'] or postingObj['pos']
    def __getitem__(self, key):
        assert key == 'positions' or key == 'pos', f"{key} does NOT exist!"
        return self._positions

    #Overload print function to print obj info
    def __repr__(self) -> str:
        wExists = False
        rStr = f'\tToken: {self._tok}\n\t\tPositions:'
        if len(self._positions) == 0:
            rStr += ' None'
        else:
            rStr += f' {self._positions}'
        return rStr
    
#Document is an object to hold doc weight and multiple postings
class Document:
    def __init__(self, docId:int) -> None:
        self._docId = docId
        self._weights = defaultdict(lambda: set())
        self._postings = defaultdict(lambda: dict)
    
    #Setter functions
    def addWeight(self, wType:str, pos:int) -> None:
        self._weights[wType].add(pos)
    
    def addPosting(self, posting: Posting):
        self._postings[posting.getToken()] = posting

    #Getter functions
    def getDocId(self):
        return self._docId

    def getWeights(self):
        return self._weights
    
    #Setter functions
    def setDocId(self, docId:int):
        self._docId = docId

    def __setitem__(self, key, newValue):
        if newValue != None:
            self._postings[key] = newValue

    #Overload bracket operator to allow accessing posting obj
    #Example: DocumentObj[tok:str]
    def __getitem__(self, key):
        #Add item if key does not exist
        if key not in self._postings:
            self._postings[key] = Posting(key)
        return self._postings[key]
    
    def printWeights(self, getStr = False) -> None | str:
        rStr = f'\tWeights:'
        if len(self._weights) == 0:
            rStr += 'None\n'
        else:
            for w in self._weights:
                rStr += f'\n\t\t{w}:{self._weights[w]}'
        if getStr: return rStr
        print(rStr)

    def __repr__(self) -> str:
        rStr = f'DocId: {self._docId}\n'
        rStr += self.printWeights(getStr=True)
        for post in self._postings:
            rStr += f'\n{self._postings[post]}'
        return rStr
    
#InvertedIndex is an object to hold multiple document objects
class InvertedIndex:
    def __init__(self) -> None:
        self._index = defaultdict(lambda: dict)
        self._size = 0

    #Setter functions
    def addDoc(self, doc:Document) -> None:
        self._index[doc.getDocId()] = doc
        self._size += 1

    #Getter functions
    #Overload bracket operator to allow accessing inverted index doc and posting obj
    #Example: InvertedIndexObj[docId:int]
    def __getitem__(self, key):
        assert key in self._index, f"Document {key} does NOT exist!"
        return self._index[key]

    def getSize(self):
        return self._size

    #Overload print function to print obj info
    def __repr__(self) -> str:
        rStr = f'Size: {self._size}\n'
        for docId in self._index:
            rStr += f'{self._index[docId]}\n'
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
    def __init__(self, *, convert_charrefs: bool = True) -> None:
        super().__init__(convert_charrefs=convert_charrefs)
        self._weights = WeightFlags()
        self._doc = Document(0)
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
                    #Create posting and add to doc
                    self._doc[token].addPosition(self._pos)

                    #Add weight and position to doc
                    for field in self._weights.getActiveFields():
                        self._doc.addWeight(field,self._pos)

                    self._pos += 1
            print(data, self._weights.getActiveFields())

    def getDoc(self):
        return self._doc