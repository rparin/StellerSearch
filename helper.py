from bs4 import UnicodeDammit
from lxml.html.clean import Cleaner
from HelperClass import InvertedIndex, HTMLTokenizer

#Decode html string
#Cite: https://lxml.de/elementsoup.html
def decode_html(html_string: str) -> str:
    """decode_html takes in an HTML string as input and attempts to
    use UniCode Dammit to detect a document's encoding and covert it to
    Unicode

    Args:
        html_string (str): A string version of the html markup

    Returns:
        str: A converted Unicode string or original HTML string
    """
    #Attempts to convert the original HTML's string to a different encoding.
    converted = UnicodeDammit(html_string) 

    #Return original string if unable to decode using library
    if not converted.unicode_markup:
        return html_string
    return converted.unicode_markup

def cleanHtml(html_content: str):
    cleaner = Cleaner(page_structure=False, meta=True, comments=True,style=True, inline_style=True, processing_instructions=True, remove_unknown_tags=True)
    decoded_html = decode_html(html_content)
    clean_html = cleaner.clean_html(decoded_html)
    return clean_html

#Cleans HTML and parses html content into tokens then adds it to Inverted index
def tokenizeHtml(docId:int, invIndex:InvertedIndex, htmlContent:str):
    parser = HTMLTokenizer(docId=docId, invIndex=invIndex) #Create parser obj
    parser.feed(cleanHtml(htmlContent)) #pass in clean html to parse
    invIndex.reCountTf() #Upate total freq