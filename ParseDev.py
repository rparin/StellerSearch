import os
import psutil
import json
import shelve
from HelperClass import InvertedIndex
from helper import tokenizeHtml

def writeDoc(docId:str, url:str):
    with shelve.open(f'DevShelve/Url', 'c') as shelf:
        shelf[str(docId)] = url
    
    docFile = open("DocId.txt", "a")
    docFile.write(f'{docId}:{url}\n')
    docFile.close()

def getDocNum():
    with shelve.open(f'DevShelve/Url', 'c') as shelf:
        if 'totalDoc' not in shelf:
            shelf['totalDoc'] = 0
        return int(shelf['totalDoc'])
    
def storeDocNum(totalDoc:int):
    with shelve.open(f'DevShelve/Url', 'c') as shelf:
        shelf['totalDoc'] = totalDoc

def readDocShelve(key):
    with shelve.open(f'DevShelve/Url', 'c') as shelf:
        return shelf[key]

def getDocUrl(docId:int):
    return 'a'
    with shelve.open(f'DevShelve/Url', 'c') as shelf:
        if str(docId) in shelf:
            return shelf[str(docId)]
        
# Opening JSON file
def getJsonData(filePath):
    jFile = open(filePath)
    data = json.load(jFile)
    enc = data['encoding']
    jFile.close()
    data = ''
    jFile = open(filePath, encoding=enc)
    data = json.load(jFile)
    jFile.close()
    url = data['url']
    htmlContent = data['content']
    return (url, htmlContent)

def isValidJsonSize(file):
    fileSize = os.path.getsize(file)/(1024*1024*1024)
    ramUsedGb = psutil.virtual_memory()[3]/1000000000
    totalRam = psutil.virtual_memory().total/(1024*1024*1024)
    if fileSize + ramUsedGb >= (totalRam * .11):
        return False
    return True

def isMemoryFull(limit=10.5):
    if psutil.virtual_memory()[2] >= limit:
       print(psutil.virtual_memory()[2])
       return True
    return False

def writeData(invIndex, docId, count):
    invIndex.write('DevHDF5', count)
    invIndex.clear()
    storeDocNum(docId)
    print("----Wrote Data to File----")

def getJsonFiles(rootDir):
    jsonFiles = []
    for root, dirs, files in os.walk(rootDir):
        for name in files:
            if name.endswith((".json")):
                full_path = os.path.join(root, name)
                jsonFiles.append(full_path)
    return jsonFiles


def main() -> None:
    rootDir = '/home/rparin/CS121/HW3/DEV'
    jsonFiles = getJsonFiles(rootDir)

    #Create inverted index to hold tokens from parser
    invIndex = InvertedIndex() 
    docId = 0
    count = 1
    for jFile in jsonFiles:
        if not isValidJsonSize(jFile):
            writeData(invIndex, docId, count)
            count += 1

        #Dont Load json file
        if not isValidJsonSize(jFile):
            docFile = open("InvalidJson.txt", "a")
            docFile.write(f'{docId}:{url}\n')
            docFile.close()
        else:
            docId += 1
            url, htmlContent = getJsonData(jFile)

            #Check if already parsed
            if url == getDocUrl(docId):
                print(f'Parsed Already -- {docId}:{url}')
            else:
                # Cleans and parses HTML content into tokens then adds it to Inverted index
                tokenizeHtml(docId=docId, invIndex=invIndex, htmlContent=htmlContent)
                print(docId, url)

                if isMemoryFull():
                    writeData(invIndex, docId, count)
                    count += 1

    if docId != getDocNum():
        writeData(invIndex, docId, count)
        count += 1

def test() -> None:
    rootDir = '/home/rparin/CS121/HW3/DEV'
    jsonFiles = getJsonFiles(rootDir)

    docId = 1
    url, htmlContent = getJsonData(jsonFiles[docId-1])
    print(url)
    invIndex = InvertedIndex() #Create inverted index to hold tokens from parser
    tokenizeHtml(docId=docId, invIndex=invIndex, htmlContent=htmlContent)
    print(invIndex)

if __name__ == "__main__":
    main()

