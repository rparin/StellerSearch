from collections import defaultdict

class Posting:
    def __init__(self, tok:str) -> None:
        self._tok = tok
        self._positions = set()
        self._weights = defaultdict(lambda: set())

    def addPosition(self, pos:int) -> None:
        self._positions.add(pos)
    
    def addWeight(self, wType:str, pos:tuple) -> None:
        self._weights[wType].add(pos)

    def __getitem__(self, key):
        if key == 'positions':
            return self._positions
        if key == 'weights':
            return self._weights
        
    def printWeights(self):
        rStr = 'Weights:'
        for w in self._weights:
            wExists = True
            rStr += f'\n\t{w}:'
            rStr += f' {self._weights[w]}'                

        if not wExists:
            rStr += ' None'
        print(rStr)
    
    def getToken(self) -> str:
        return self._tok

    def __repr__(self) -> str:
        wExists = False
        rStr = f'\tToken: {self._tok}\n\t\tPositions:'
        if len(self._positions) == 0:
            rStr += ' None'
        else:
            rStr += f' {self._positions}'
        
        rStr += '\n\t\tWeights:'

        for w in self._weights:
            wExists = True
            rStr += f'\n\t\t\t{w}:'
            rStr += f' {self._weights[w]}'                

        if not wExists:
            rStr += ' None'
        return rStr

class InvertedIndex:
    def __init__(self) -> None:
        self._index = defaultdict(lambda: defaultdict(lambda: dict))
        self._idCount = 1

    def addTokenPosting(self,posting: Posting) -> None:
        self._index[self._idCount][posting.getToken()] = posting

    def incDocId(self) -> None:
        self._idCount += 1

    def __getitem__(self, key):
        return self._index[key]

    def printDoc(self, docId:int) -> None:
        if not docId in self._index:
            print('Does not Exist')
            return
        
        rStr = ''
        rStr += f'DocId: {docId}\n'
        for tok in self._index[docId]:
            rStr += f'{self._index[docId][tok]}'
            rStr += '\n'
        print(rStr)

    def __repr__(self) -> str:
        rStr = ''
        for docId in self._index:
            rStr += f'DocId: {docId}\n'
            for tok in self._index[docId]:
                rStr += f'{self._index[docId][tok]}'
                rStr += '\n'
        rStr += '\n'
        return rStr