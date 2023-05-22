import pandas as pd
import warnings

def df_from_dict(dictObj:dict):
    df = pd.DataFrame.from_dict(dictObj, orient='index')
    return df.transpose()

def main():
    warnings.filterwarnings('ignore')
    with open("docId.txt") as inFile:
        for line in inFile:
            parsed = line.split()
            docId = parsed[0]
            df = df_from_dict({docId:parsed[1]})
            df.to_hdf(f'DevHDF5/Url.hdf5', key=docId)
            print(docId)

if __name__ == "__main__":
    main()
# Access term cell: df.iat[0, 0]