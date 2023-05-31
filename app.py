from flask import Flask, render_template, request
from flask_paginate import Pagination, get_page_parameter
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
        "https://www.pokemon.com/us/pokedex/ivysaur",
        "https://www.pokemon.com/us/pokedex/venusaur",
        "https://www.pokemon.com/us/pokedex/charmander",
        "https://www.pokemon.com/us/pokedex/charmeleon",
        "https://www.pokemon.com/us/pokedex/charizard",
        "https://www.pokemon.com/us/pokedex/squirtle",
        "https://www.pokemon.com/us/pokedex/wartortle",
        "https://www.pokemon.com/us/pokedex/blastoise",
        "https://www.pokemon.com/us/pokedex/caterpie",
        "https://www.pokemon.com/us/pokedex/metapod",
        "https://www.pokemon.com/us/pokedex/butterfree",
        "https://www.pokemon.com/us/pokedex/weedle",
        "https://www.pokemon.com/us/pokedex/kakuna",
    ]

    page = request.args.get(get_page_parameter(), type=int, default=1)
    offset_num_page = (page - 1) * 10
    paginated_urls = urls[offset_num_page:offset_num_page + 10]
    results = [(url, summarize_url(url)) for url in paginated_urls]

    pagination = Pagination(page=page, total=len(urls), urls_per_page=10)

    return render_template("index.html", results=results, pagination=pagination)

if __name__ == "__main__":
    app.run(debug=True)
