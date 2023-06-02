from flask import Flask, render_template, request, jsonify 
import openai

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
    urls = [
        'https://www.pokemon.com/us/pokedex/charmander'
    ]
    userQuery = request.form.get("searchQuery")
    return render_template("searchResults.html", resultLen = len(urls), results = urls, userQuery = userQuery)

if __name__ == "__main__":
    app.run(debug=True)
