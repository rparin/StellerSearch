from bs4 import UnicodeDammit
from lxml.html.clean import Cleaner

#Decode html string
#Cite: https://lxml.de/elementsoup.html
def decode_html(html_string):
    converted = UnicodeDammit(html_string)

    #Return original string if unable to decode using library
    if not converted.unicode_markup:
        return html_string
    return converted.unicode_markup

def cleanHtml(html_content):
    cleaner = Cleaner(page_structure=False, meta=True, comments=True,style=True, inline_style=True, processing_instructions=True, remove_unknown_tags=True)
    decoded_html = decode_html(html_content)
    clean_html = cleaner.clean_html(decoded_html)
    return clean_html