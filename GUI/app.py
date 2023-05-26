from flask import Flask, render_template

# https://www.geeksforgeeks.org/live-search-using-flask-and-jquery/#
app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
