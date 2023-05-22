import pandas as pd
import warnings

def df_from_dict(dictObj:dict):
    df = pd.DataFrame.from_dict(dictObj, orient='index')
    return df.transpose()

def main():
    warnings.filterwarnings('ignore')
    docUrl = {}
    start = 4485
    with open("docId.txt") as inFile:
        for line in inFile:
            parsed = line.split()
            if int(parsed[0]) > start:
                docUrl[int(parsed[0])] = parsed[1]
            
    for docId in docUrl:
        df = df_from_dict({docId:docUrl[docId]})
        df.to_hdf(f'DevHDF5/Url2.hdf5', key=str(docId))
        print(docId, docUrl[docId])


if __name__ == "__main__":
    main()
    # docId = 4485
    # df = pd.read_hdf('DevHDF5/Url.hdf5', str(docId))
    # print(docId, df.iat[0, 0])
# Access term cell: df.iat[0, 0]