import pandas as pd
from bs4 import UnicodeDammit
from lxml.html.clean import Cleaner
from HelperClass import InvertedIndex, HTMLTokenizer, Token

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

def df_from_dict(token:Token):
    df = pd.DataFrame.from_dict(token.getAllPos(), orient='index')
    df.fillna(0, inplace=True)
    df = df.astype('int32')
    return df.transpose()

#Cite: https://stackoverflow.com/questions/47545052/convert-dataframe-rows-to-python-set
def dict_from_df(df) -> dict:
    df = df.transpose()
    series_set = df.apply(frozenset, axis=1)
    new_df = series_set.apply(lambda a: set(a))
    return dict(new_df)

def join_df_col(df1,df2):
    df3 = df1.join(df2)
    df3.fillna(0, inplace=True)
    return df3.astype('int32')