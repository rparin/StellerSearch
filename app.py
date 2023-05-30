from flask import Flask, render_template
import openai

# Citation: https://www.geeksforgeeks.org/live-search-using-flask-and-jquery/#
app = Flask(__name__)

openai.api_key = "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"

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


@app.route("/")
def home():
    urls = [
        "https://www.pokemon.com/us/pokedex/bulbasaur",
        "https://www.pokemon.com/us/pokedex/charmander",
        "https://www.pokemon.com/us/pokedex/squirtle",
    ]
    results = [(url, summarize_url(url)) for url in urls]
    return render_template("index.html", results=results)


if __name__ == "__main__":
    app.run(debug=True)
