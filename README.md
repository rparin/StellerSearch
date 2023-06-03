<div align="center">

# Steller Search

[![License][license.io]][license-url]

<p align="left">
Steller Search is a search engine built using the Python programming language and the Flask web framework. This search engine provides users with the ability to search for information within a given dataset or collection of documents.
</p>

[About](#about) •
[Running the Search Engine](#running-the-search-engine) •
[Technologies](#technologies) •
[Credits](#credits) •
[License](#license)

</div>

## About

<div align="center">

<img height=350 alt="demo of Search Engine" src="https://imgur.com/a/tPPq2An">

</div>

### Features

- Fast and accurate results < 300ms
- Navigate through multiple results
- Use of Open AI to display url summary

## Running the Search Engine

⚠️ **Note:** Before you are able to run the search engine ensure that you have the following packages installed and a valid Open AI key

```
pip install Flask, Flask-Session, lxml, pandas, pyarrow, PorterStemmer, openai, pyspellchecker
```

1. To run the flask gui simply run the command

```
python app.py
```

## Technologies

<div align="center">

[![OpenAi][openai.io]][openai-url] [![Flask][flask.io]][flask-url] [![Pandas][pandas.io]][pandas-url]

</div>

## Credits

This search engine was made by me and my fellow group partners, [Letsy][letsy-url], [Yizhou][yizhou-url], [Geanie][geanie-url].

## License

This project is licensed under the MIT License - see the [LICENSE][git-license-url] file for details.

<!-- MARKDOWN LINKS & IMAGES -->

[license.io]: https://img.shields.io/badge/license-MIT-blue.svg
[license-url]: https://opensource.org/licenses/MIT
[git-license-url]: https://github.com/rparin/A3WebSearch/blob/main/LICENSE
[pandas.io]: https://img.shields.io/badge/Pandas-130654?style=for-the-badge&logo=pandas&logoColor=#130654
[pandas-url]: https://pandas.pydata.org/
[flask.io]: https://img.shields.io/badge/Flask-FFFFFF?style=for-the-badge&logo=flask&logoColor=black
[flask-url]: https://flask.palletsprojects.com/
[openai.io]: https://img.shields.io/badge/OpenAi-000000?style=for-the-badge&logo=openai&logoColor=white
[openai-url]: https://platform.openai.com/
[letsy-url]: https://github.com/Galetsy
[yizhou-url]: https://github.com/yizhoc4
[geanie-url]: https://github.com/geesants
