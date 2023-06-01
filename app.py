from flask import Flask, render_template
import openai
import requests

# Citation: https://www.geeksforgeeks.org/live-search-using-flask-and-jquery/#
app = Flask(__name__)


@app.route("/")
def home():

    result_urls = ["ics.uci.edu", "cs.uci.edu", "informatics.uci.edu", "stat.uci.edu"]

    summaries = []
    for url in result_urls:
        response = requests.get(url)
        text = response.text
        summary = generate_summary(text)
        summaries.append(summary)

    return render_template("index.html", result_urls=result_urls, summaries=summaries)

    


# Cited from: https://medium.com/muthoni-wanyoike/implementing-text-summarization-using-openais-gpt-3-api-dcd6be4f6933

openai.api_key = "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"


def preprocess(url):

    max_chunk_size = 2048
    chunks = []
    current_chunk = ""
    for sentence in text.split("."):
        if len(current_chunk) + len(sentence) < max_chunk_size:
            current_chunk += sentence + "."
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + "."
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks
    return 0


def generate_summary(text):
    input_chunks = preprocess(text)
    output_chunks = []
    for chunk in input_chunks:
        response = openai.Completion.create(
            engine="davinci",
            prompt=(f"Please summarize the following text:\n{chunk}\n\nSummary:"),
            temperature=0.5,
            max_tokens=1024,
            n = 1,
            stop=None
        )
        summary = response.choices[0].text.strip()
        output_chunks.append(summary)
    return " ".join(output_chunks)




if __name__ == "__main__":
    app.run(debug=True)

