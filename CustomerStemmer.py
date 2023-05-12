from nltk.stem import SnowballStemmer

class CustomerStemmer(SnowballStemmer):
    def __init__(self, language, ignore_stopwords=False):
        super().__init__(language, ignore_stopwords)
        self.rules = {"ies": "y"}

    def customStem(self, token):
        for suffix, replSuffix in self.rules.items():
            if token.endswith(suffix):
                notSuffix = token[:-len(suffix)]
                if len(notSuffix) > 1:
                    token = notSuffix + replSuffix
                    return token
        stemmer = SnowballStemmer(language="english")
        return stemmer.stem(token)    


if __name__ == "__main__":
    stemmer = CustomerStemmer("english")
    custTest = stemmer.customStem("happier")
    print(custTest)

    stemmer = SnowballStemmer("english")
    snowTest = stemmer.stem("happier")
    print(snowTest)

# Success:
# parties, cries, supplies

# Failure:
# aggies, disconformities(?)
