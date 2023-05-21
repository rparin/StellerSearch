import warnings
warnings.filterwarnings('ignore')
from HelperClass import InvertedIndex
import pandas as pd

def df_from_dict(dictObj:dict, toInt = False):
    df = pd.DataFrame.from_dict(dictObj, orient='index')
    df.fillna(0, inplace=True)
    if toInt: df = df.astype('int32')
    return df

def storeTermDf(invIndex, term):
    docDict = {}
    termDf = None
    start = True
    for docId in invIndex['pos'][term]:
        pos = invIndex['pos'][term][docId]
        if start:
            termDf = df_from_dict({1:{docId: pos}})
            start = False
        else:
            newDf = df_from_dict({1:{docId: pos}})
            termDf = pd.concat([termDf, newDf.transpose()])
    termDf = termDf.transpose()
    termDf.to_hdf(f'DevHDF5/Terms.hdf5', key=term)
    return termDf

def main():
    invIndex = InvertedIndex()
    invIndex.loadAll()
    count = 1
    for term in invIndex['pos']:
        count += 1
        storeTermDf(invIndex,term)
        print(count, term)
