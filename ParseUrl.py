import pandas as pd
import warnings

def df_from_dict(dictObj:dict):
    df = pd.DataFrame.from_dict(dictObj, orient='index')
    return df.transpose()

def main():
    warnings.filterwarnings('ignore')
    docUrl = {}

    with open("docId.txt") as inFile:
        for line in inFile:
            parsed = line.split()
            docUrl[int(parsed[0])] = parsed[1]
            
    for docId in docUrl:
        df = df_from_dict({docId:docUrl[docId]})
        df.to_hdf(f'DevHDF5/Url.hdf5', key=str(docId))
        print(docId)


if __name__ == "__main__":
    main()
# Access term cell: df.iat[0, 0]