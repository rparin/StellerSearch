from flask import Flask, request, render_template, session
from flask_session import Session
from HelperClass import QueryParser
import openai
import time
import sys

# Citation: https://www.geeksforgeeks.org/how-to-use-flask-session-in-python-flask/#
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
openai.api_key = 'YOUR-OPEN-API-Key'

# Citation: https://platform.openai.com/examples/default-tldr-summary
def summarize_url(url):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Summarize the content from {url}",
        temperature=0.7,
        max_tokens=80,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=1
    )
    summary = response.choices[0].text.strip()
    period_in_sum = summary.rfind('.')
    if period_in_sum != -1:
        summary = summary[:period_in_sum+1]
    return summary

def calculatePage(queryParser, isNext):
    pages = session['pages']
    currentPage = session['currentPage']
    avoid = session['avoid']
    userQuery = session['userQuery']

    if isNext: 
        currentPage += 1 
    else:
        currentPage -= 1

    if currentPage == 0:
        currentPage = 1

    urls = []
    start = time.time_ns()
    if currentPage in pages: 
        urls = pages[currentPage]
    else:
        results = queryParser.runQuery(userQuery, avoid)
        for tup in results:
            urls.append(queryParser._getDocData(int(tup[1]))['url'])
            avoid.add(tup[1])
        pages[currentPage] = urls 
    end = time.time_ns()
    timeE = round((end - start) / (10**6),3) #Time in milliseconds

    session['pages'] = pages
    session['currentPage'] = currentPage
    session['avoid'] = avoid
    session['userQuery'] = userQuery
    return timeE, urls


@app.route("/", methods =["GET", "POST"])
def home():
    global indexFp
    global docIdFp
    global indexFile
    global docFile
    global queryParser

    #Open Index of Index files
    indexFp = open("Data/indexFp.feather", "rb")
    docIdFp = open("Data/docIdFp.feather", "rb")

    #Open index files
    indexFile = open('Data/Index.txt', "r")
    docFile = open('Data/docId.txt', "r")

    #Create query parser obj
    queryParser = QueryParser(indexFp, docIdFp, indexFile, docFile)
    queryParser.runQuery('test')

    # results = [(url, summarize_url(url)) for url in urls]
    # return render_template("index.html", resultLen = len(urls), results = results)
    return render_template("home.html")

@app.route('/query', methods=['POST']) 
def query(): 

    #Keep track of url page search
    pages = {}
    urls = []
    currentPage = 1
    avoid = set()
    userQuery = request.form.get("searchQuery")
    start = time.time_ns()
    results = queryParser.runQuery(userQuery, avoid)
    for tup in results:
        urls.append(queryParser._getDocData(int(tup[1]))['url'])
        avoid.add(tup[1])
    end = time.time_ns()
    pages[currentPage] = urls

    session['pages'] = pages
    session['currentPage'] = currentPage
    session['avoid'] = avoid
    session['userQuery'] = userQuery

    timeE = round((end - start) / (10**6),3) #Time in milliseconds
    return render_template("searchResults.html", resultLen = len(urls), results = urls, userQuery = userQuery, timeElapsed = timeE, curPage = session['currentPage'])

@app.route('/next', methods =["GET", "POST"]) 
def nextPage():
    timeE, urls = calculatePage(queryParser, True)
    return render_template("searchResults.html", resultLen = len(urls), results = urls, userQuery = session['userQuery'], timeElapsed = timeE, curPage = session['currentPage'])

@app.route('/prev', methods =["GET", "POST"]) 
def prevPage():
    timeE, urls = calculatePage(queryParser, False)
    return render_template("searchResults.html", resultLen = len(urls), results = urls, userQuery = session['userQuery'], timeElapsed = timeE, curPage = session['currentPage'])

if __name__ == "__main__":
    app.run(debug=True)
