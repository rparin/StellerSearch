###How to run the indexer

Before running the indexer make sure to have these packages installed.
```
pip install lxml, pandas, pyarrow, PorterStemmer, pyspellchecker
```

## Creating partial Indexes
1. Open the 'ParseDev.py' file
2. Create a Data folder in the same directory as 'ParseDev.py', this Data folder will be populated with partial indexes.
3. Run ParseDev.py python program

## Merging the partial Indexes
1. After getting the partial indexes open the IndexMerge.ipynb file and run the notebook
2. This will create a merged index in the Data folder called 'Index.txt'

## Running a simple query
1. Open the Query.ipynb notebook file
2. Modify the query variable to your desired query phrase
3. Run the notebook

## Running the flask gui
1. Ensure that you have all of the packages below installed
```
pip install Flask, Flask-Session, openai
```
1. In the terminal run the command
```
python app.py
```
2. Open the localhost port that shows up in your terminal