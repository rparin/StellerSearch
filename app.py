from flask import Flask, render_template, request, jsonify
from HelperClass import QueryParser
import openai
import time

#Open Index of Index files
indexFp = open("Data/indexFp.feather", "rb")
docIdFp = open("Data/docIdFp.feather", "rb")

#Open index files
indexFile = open('Data/Index.txt', "r")
docFile = open('Data/docId.txt', "r")

#Create query parser obj
queryParser = QueryParser(indexFp, docIdFp, indexFile, docFile)

# Citation: https://www.geeksforgeeks.org/live-search-using-flask-and-jquery/#
app = Flask(__name__)

openai.api_key = 'REMOVED'

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


@app.route("/", methods =["GET", "POST"])
def home():
    # results = [(url, summarize_url(url)) for url in urls]
    # return render_template("index.html", resultLen = len(urls), results = results)
    return render_template("home.html")

@app.route('/query', methods=['POST']) 
def query(): 
    urls = []
    userQuery = request.form.get("searchQuery")
    start = time.time_ns()
    avoid = {}
    results = queryParser.runQuery(userQuery, avoid)
    for tup in results:
        urls.append(queryParser._getDocData(int(tup[1]))['url'])
    end = time.time_ns()

    timeE = round((end - start) / (10**6),2) #Time in milliseconds
    return render_template("searchResults.html", resultLen = len(urls), results = urls, userQuery = userQuery, timeElapsed = timeE)

if __name__ == "__main__":
    app.run(debug=True)
