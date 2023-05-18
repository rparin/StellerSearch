from nltk.stem.porter import PorterStemmer
from nltk.stem.snowball import SnowballStemmer

stemmer = PorterStemmer()
l = stemmer.stem("ran")
print(l)

stemmer = SnowballStemmer("english")
a = stemmer.stem("ran")
print(a)