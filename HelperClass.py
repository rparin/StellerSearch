from collections import defaultdict

class Posting:
    def __init__(self, tok:str) -> None:
        self.tok = tok
        self.positions = set()
        self.weights = defaultdict(lambda: set())

    def addPosition(self, pos:int) -> None:
        self.positions.add(pos)
    
    def addWeight(self, type:str, pos:tuple) -> None:
        self.weights[type].add(pos)
    
    def getToken(self) -> str:
        return self.tok

    def __repr__(self) -> str:
        wExists = False
        rStr = f'\tToken: {self.tok}\n\t\tPositions:'
        if len(self.positions) == 0:
            rStr += ' None'
        else:
            rStr += f' {self.positions}'
        
        rStr += '\n\t\tWeights:'

        for w in self.weights:
            wExists = True
            rStr += f'\n\t\t\t{w}:'
            rStr += f' {self.weights[w]}'                

        if not wExists:
            rStr += ' None'
        else:
            rStr += '\n'

        return rStr

class InvertedIndex:
    def __init__(self) -> None:
        self._index = defaultdict(lambda: defaultdict(lambda: dict))
        self.idCount = 1

    def addTokenPosting(self,posting: Posting) -> None:
        self._index[self.idCount][posting.getToken()] = posting

    def incDocId(self) -> None:
        self.idCount += 1

    def __repr__(self) -> str:
        rStr = ''
        for docId in self._index:
            rStr += f'DocId: {docId}\n'
            for tok in self._index[docId]:
                rStr += f'{self._index[docId][tok]}'
                rStr += '\n'
        rStr += '\n'

        return rStr