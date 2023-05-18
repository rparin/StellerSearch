from lxml.html.clean import Cleaner
from HelperClass import InvertedIndex, HTMLTokenizer
import lxml.html
import lxml.html.soupparser
from lxml.etree import tostring

#Cite: https://lxml.de/elementsoup.html
def cleanHtml(html_content):
    cleaner = Cleaner(page_structure=False, meta=True, comments=True,style=True, inline_style=True, processing_instructions=True, remove_unknown_tags=True)

    root = lxml.html.fromstring(html_content)
    try:
        ignore = tostring(root, encoding='unicode')
    except UnicodeDecodeError:
        root = lxml.html.soupparser.fromstring(html_content)

    clean_html = cleaner.clean_html(str(tostring(root)))
    return clean_html

#Cleans HTML and parses html content into tokens then adds it to Inverted index
def tokenizeHtml(docId:int, invIndex:InvertedIndex, htmlContent:str):
    parser = HTMLTokenizer(docId=docId, invIndex=invIndex) #Create parser obj
    parser.feed(cleanHtml(htmlContent)) #pass in clean html to parse
    invIndex.reCountTf() #Update total freq