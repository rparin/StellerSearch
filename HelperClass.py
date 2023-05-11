from collections import defaultdict

class Posting:
    def __init__(self, tok:str) -> None:
        self.tok = tok
        self.positions = set()
        self.weights = defaultdict(lambda: set())

    def addPosition(self, pos:int) -> None:
        self.positions.add(pos)
    
    def addWeight(self, wType:str, pos:tuple) -> None:
        self.weights[wType].add(pos)
    
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
        return rStr

class InvertedIndex:
    def __init__(self) -> None:
        self._index = defaultdict(lambda: defaultdict(lambda: dict))
        self.idCount = 1

    def addTokenPosting(self,posting: Posting) -> None:
        self._index[self.idCount][posting.getToken()] = posting

    def incDocId(self) -> None:
        self.idCount += 1

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