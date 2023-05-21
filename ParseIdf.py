from HelperClass import InvertedIndex
import math
import warnings
warnings.filterwarnings('ignore')

def calculate_idf(df, N = 55382):
    idf = math.log((N + 0.1) / (df + 0.1))
    return idf

import pandas as pd
def df_from_dict(dictObj:dict):
    df = pd.DataFrame.from_dict(dictObj, orient='index')
    return df.transpose()

def main():
    invIndex = InvertedIndex()
    invIndex.loadAll('DevShelve')
    count = 0
    for term in invIndex['pos']:
        dfCount = len(invIndex['pos'][term])
        idf = calculate_idf(dfCount)
        df = df_from_dict({term:idf})
        df.to_hdf(f'DevHDF5/Idf.hdf5', key=term)
        count += 1
        print(count, term)

if __name__ == "__main__":
    main()
# Access term cell: df.iat[0, 0]
