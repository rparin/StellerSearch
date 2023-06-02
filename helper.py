from bs4 import UnicodeDammit
from lxml.html.clean import Cleaner
from HelperClass import InvertedIndex, HTMLTokenizer
import pyarrow.feather as feather
import json

#Decode html string
#Cite: https://lxml.de/elementsoup.html
def decode_html(html_string):
    converted = UnicodeDammit(html_string)

    #Return original string if unable to decode using library
    if not converted.unicode_markup:
        return html_string
    return converted.unicode_markup

def cleanHtml(html_content) -> str:
    cleaner = Cleaner(page_structure=False, meta=True, comments=True,style=True, inline_style=True, processing_instructions=True, remove_unknown_tags=True)
    try:
        decoded_html = decode_html(html_content)
        clean_html = cleaner.clean_html(decoded_html)
        return clean_html
    except:
        try:
            clean_html = cleaner.clean_html(html_content.encode())
            return str(clean_html)
        except:
            return None

#Cleans HTML and parses html content into tokens then adds it to Inverted index
def tokenizeHtml(docId:int, invIndex:InvertedIndex, htmlContent:str):
    parser = HTMLTokenizer(docId=docId, invIndex=invIndex) #Create parser obj
    clean_html = cleanHtml(htmlContent)
    if clean_html:
        parser.feed(clean_html) #pass in clean html to parse
    return parser.getDocLen()


def getFpDataframe(fileName:str):
    fpDf = None
    with open(f'Data/{fileName}.feather', 'rb') as f:
        fpDf = feather.read_feather(f)
    return fpDf

def getTermData(term:str, fpDf):
    termInfo = None
    if term not in fpDf['fp']: return termInfo
    with open(f'Data/Index.txt', "r") as indexFile:
        indexFile.seek(fpDf['fp'][term])
        tInfo = indexFile.readline().strip().split('>')[1]
        return json.loads(tInfo) 

def getDocData(docId:int, fpDf):
    docInfo = None
    if docId not in fpDf['fp']: return docInfo
    with open(f'Data/docId.txt', "r") as indexFile:
        indexFile.seek(fpDf['fp'][docId])
        tInfo = indexFile.readline().strip().split('>')[1]
        return json.loads(tInfo) 