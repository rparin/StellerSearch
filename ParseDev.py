import os
import psutil
import json
import shelve
from HelperClass import InvertedIndex
from helper import tokenizeHtml

#Save doc information to txt file
#Called every time doc parsed
def writeDoc(docId:str, url:str, docLen:int):
    docJson = json.dumps({'url': url, 'docLen':docLen})
    docFile = open("Data/docId.txt", "a")
    docFile.write(f'{docId}>{docJson}\n')
    docFile.close()

#Store number of documents parsed to shelve file
#Called once at the end to see if index write complete
def getDocNum():
    with shelve.open(f'Data/Url', 'c') as shelf:
        if 'totalDoc' not in shelf:
            shelf['totalDoc'] = 0
        return int(shelf['totalDoc'])
    
#Grab number of documents parsed
#Called every time index writes to a file
def storeDocNum(totalDoc:int):
    with shelve.open(f'Data/Url', 'c') as shelf:
        shelf['totalDoc'] = totalDoc
        
# Opening JSON file using encoding in JSON file
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

#Before opening json file check if there's enough memory to hold json data
def isValidJsonSize(file):
    fileSize = os.path.getsize(file)/(1024*1024*1024)
    ramUsedGb = psutil.virtual_memory()[3]/1000000000
    totalRam = psutil.virtual_memory().total/(1024*1024*1024)
    if fileSize + ramUsedGb >= (totalRam * .70):
        return False
    return True

#Set threshold of 70% ram capacity, write to file once threshold reached
def isMemoryFull(limit=70):
    if psutil.virtual_memory()[2] >= limit:
       print(psutil.virtual_memory()[2])
       return True
    return False

#Write inverted index to file and clear index
def writeData(invIndex, docId, count):
    invIndex.write('Data', count)
    invIndex.clear()
    storeDocNum(docId)
    print("----Wrote Data to File----")

#Get all json files in dev folder
def getJsonFiles(rootDir):
    jsonFiles = []
    for root, dirs, files in os.walk(rootDir):
        for name in files:
            if name.endswith((".json")):
                full_path = os.path.join(root, name)
                jsonFiles.append(full_path)
    return jsonFiles

# Go through all json files and create partial inverted Index
def main() -> None:
    rootDir = 'DIRECTORY/TO/JSON/HTML/CONTENT/FOLDER'
    jsonFiles = getJsonFiles(rootDir)

    #Create inverted index to hold tokens from parser
    invIndex = InvertedIndex() 
    docId = 1
    count = 1
    for jFile in jsonFiles:
        #Write to file to save memory for next json
        if not isValidJsonSize(jFile):
            if len(invIndex['pos']) != 0:
                writeData(invIndex, docId, count)
                writeDoc(docId, url, docLen)
                invIndex.clear()
                invIndex = InvertedIndex() 
                count += 1
                docId += 1
        else:
            #Dont Load json file, still too big after memory clear
            if not isValidJsonSize(jFile):
                docFile = open("InvalidJson.txt", "a")
                docFile.write(f'{docId} {url}\n')
                docFile.close()
            else:
                skip = False
                #Encoding issue with reading json
                try:
                    url, htmlContent = getJsonData(jFile)
                except:
                    #Dont parse html if error
                    #Log the invalid json file
                    docFile = open("HTMLContentErr.txt", "a")
                    docFile.write(f'{jFile}\n')
                    docFile.close()
                    skip = True

                if skip:
                    print(f'Encoding issue -- {jFile}')
                else:
                    # Cleans and parses HTML content into tokens then adds it to Inverted index
                    docLen = tokenizeHtml(docId=docId, invIndex=invIndex, htmlContent=htmlContent)
                    writeDoc(docId, url, docLen)
                    print(docId, url)
                    
                    #Write partial index to file if memory threshold reached
                    if isMemoryFull():
                        writeData(invIndex, docId, count)
                        count += 1
                        invIndex.clear()
                        invIndex = InvertedIndex() 

                    docId += 1
                    
    #After parsing all documents check if write to file is needed
    if docId != getDocNum():
        writeData(invIndex, docId, count)
        count += 1
        invIndex.clear()
        invIndex = InvertedIndex()
    else:
        print(f'----Parsed Already----- {docId}, {url}')

if __name__ == "__main__":
    main()