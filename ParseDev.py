import os
import json
import shelve
from HelperClass import InvertedIndex
from helper import tokenizeHtml

def writeDoc(docId:str, url:str):
    with shelve.open(f'DevShelve/DocId', 'c') as shelf:
        shelf[str(docId)] = url

def getDocNum():
    with shelve.open(f'DevShelve/DocId', 'c') as shelf:
        if 'totalDoc' not in shelf:
            shelf['totalDoc'] = 0
        return int(shelf['totalDoc'])
    
def storeDocNum(totalDoc:int):
    with shelve.open(f'DevShelve/DocId', 'c') as shelf:
        shelf['totalDoc'] = totalDoc

def readDocShelve(key):
    with shelve.open(f'DevShelve/DocId', 'c') as shelf:
        return shelf[key]
    
# Opening JSON file
def getJsonData(filePath):
    jFile = open(filePath)
    data = json.load(jFile)
    url = data['url']
    htmlContent = data['content']
    jFile.close()
    return (url, htmlContent)


def main() -> None:
    rootDir = '/home/rparin/CS121/HW3/DEV'
    jsonFiles = []
    for root, dirs, files in os.walk(rootDir):
        for name in files:
            if name.endswith((".json")):
                full_path = os.path.join(root, name)
                jsonFiles.append(full_path)

    invIndex = InvertedIndex() #Create inverted index to hold tokens from parser
    docId = getDocNum()
    for jFile in jsonFiles:
        docId += 1
        url, htmlContent = getJsonData(jFile)
        # Cleans and parses HTML content into tokens then adds it to Inverted index
        tokenizeHtml(docId=docId, invIndex=invIndex, htmlContent=htmlContent)
        invIndex.write('DevShelve')
        invIndex.clear()
        writeDoc(docId, url)
        storeDocNum(docId)
        print(docId, url)

if __name__ == "__main__":
    main()

