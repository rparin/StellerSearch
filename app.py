from flask import Flask, request, render_template, session
from flask_session import Session
from HelperClass import QueryParser
import openai
import time

# Citation: https://www.geeksforgeeks.org/how-to-use-flask-session-in-python-flask/#
app = Flask(__name__)

#Create a session to store query variables
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#Open api key to get summaries for urls
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

#Decide whether if we have visited a new page if so run the query
#Retrieve old calculations and display them to the user
def calculatePage(queryParser, isNext):

    #Get values from session
    pages = session['pages']
    currentPage = session['currentPage']
    avoid = session['avoid']
    userQuery = session['userQuery']

    #Calculate if we go forward or backward a page
    if isNext: 
        currentPage += 1 
    else:
        currentPage -= 1
    
    if currentPage == 0:
        currentPage = 1

    urls = [] #Store urls to display to user
    start = time.time_ns() #Start a timer to keep track of query duration

    #Do not recalculate query if we calculated it already
    if currentPage in pages: 
        urls = pages[currentPage]
    else:
        #New page therefore run query to get new results
        #Pass in avoid list to not return results we already found
        results = queryParser.runQuery(userQuery, avoid)

        #Add results to url list and avoid set
        for tup in results:
            urls.append(queryParser._getDocData(int(tup[1]))['url'])
            avoid.add(tup[1])

        #Save calculated query as a page
        pages[currentPage] = urls 
    end = time.time_ns()

    #Query done, calculate duration
    timeE = round((end - start) / (10**6),3) #Time in milliseconds

    #Store query variables to session, to use for next query
    session['pages'] = pages
    session['currentPage'] = currentPage
    session['avoid'] = avoid
    session['userQuery'] = userQuery

    #return query duration and urls for query
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

    #Show user the home page of the search engine
    return render_template("home.html")

@app.route('/query', methods=['POST']) 
def query(): 

    #Calculate the first page of results for a given query

    #Create variables to store query information
    pages = {}
    urls = []
    currentPage = 1
    avoid = set()

    #Get userQuery from input field
    userQuery = request.form.get("searchQuery")

    #Start query duration clock
    start = time.time_ns()

    #get top documents for a given query 
    results = queryParser.runQuery(userQuery, avoid)

    #Store results in url list and avoid list to avoid recalculating later on
    for tup in results:
        urls.append(queryParser._getDocData(int(tup[1]))['url'])
        avoid.add(tup[1])

    #Query done, calculate duration
    end = time.time_ns()

    #Save calculated urls to a page
    pages[currentPage] = urls

    #Store query variables to session, to use for next query
    session['pages'] = pages
    session['currentPage'] = currentPage
    session['avoid'] = avoid
    session['userQuery'] = userQuery

    #Calculate query duration and display results to user
    timeE = round((end - start) / (10**6),3) #Time in milliseconds
    return render_template("searchResults.html", resultLen = len(urls), results = urls, userQuery = userQuery, timeElapsed = timeE, curPage = session['currentPage'])

@app.route('/next', methods =["GET", "POST"]) 
def nextPage():
    #Calculate query duration and display results to user
    timeE, urls = calculatePage(queryParser, True)
    return render_template("searchResults.html", resultLen = len(urls), results = urls, userQuery = session['userQuery'], timeElapsed = timeE, curPage = session['currentPage'])

@app.route('/prev', methods =["GET", "POST"]) 
def prevPage():
    #Calculate query duration and display results to user
    timeE, urls = calculatePage(queryParser, False)
    return render_template("searchResults.html", resultLen = len(urls), results = urls, userQuery = session['userQuery'], timeElapsed = timeE, curPage = session['currentPage'])

#Use Open Ai to get a summary given a url
@app.route('/summary', methods=['POST']) 
def getSummary():
    url = request.form.get('data')
    return summarize_url(url)

if __name__ == "__main__":
    app.run(debug=True)
