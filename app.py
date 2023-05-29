from flask import Flask, render_template

# Citation: https://www.geeksforgeeks.org/live-search-using-flask-and-jquery/#
app = Flask(__name__)


@app.route("/")
def home():
    urls = [
        "https://www.pokemon.com/us/pokedex/bulbasaur",
        "https://www.pokemon.com/us/pokedex/charmander",
        "https://www.pokemon.com/us/pokedex/squirtle",
    ]
    return render_template("index.html", urls=urls)


if __name__ == "__main__":
    app.run(debug=True)
