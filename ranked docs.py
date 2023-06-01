import math

# compute idf of a token  *idfs are the same for the same token, only depend on the df and N in docs
def calculate_idf(N, df):
    idf = math.log((N + 0.1) / (df + 0.1))
    return idf

#comupte tfidf by tf and idf    
def calculate_tfidf(tf, idf):   
    return tf*idf

#compute cosine_similarity bewteen query vector and doc vector,support any lenth
def calculate_cosine_similarity(vector_query,vector_doc):
    dot_product = sum(q * d for q, d in zip(vector_query, vector_doc))
    norm_query = math.sqrt(sum(q * q for q in vector_query))
    norm_doc = math.sqrt(sum(d * d for d in vector_doc))

    return dot_product / ((norm_query * norm_doc)+0.1)

#create query vector, query is like "fox dog", idf_dict is like {"fox":idf of fox,"dog":idf of dog}
def create_query_vector(query, idf_dict):
    #tokenize the query using our tokenizor!!!
    words = query.split()
    query_vector = []

    # Calculate TF-IDF for each word in the query
    for word in words:
        tf = words.count(word) / len(words)
        idf = idf_dict.get(word, 0)# Get IDF from the IDF dictionary (assuming it's already computed, you can just store df and N, and use calculate_idf to compute idf)
        tf_idf = tf * idf
        query_vector.append(tf_idf)

    return query_vector

#create doc vectors, like {'doc1': [0.2556430078148932, 0.10177675964835226], 'doc2': [0.0, 0.30533027894505677]}
def create_doc_vector(query, query_vector, inverted_index_tfs, idf_dict):
    doc_vectors = {}

    # Iterate over tokens in the query
    # also replace with our tokenizors!!!
    for token in query.split():
        # Check if the token exists in the inverted index postings
        if token in inverted_index_tfs:
            postings = inverted_index_tfs[token]

            # Iterate over the document IDs and TF values in the postings
            for doc_id, tf in postings.items():
                # Check if the document ID already has a vector
                if doc_id not in doc_vectors:
                    doc_vectors[doc_id] = [0] * len(query_vector)

                # Set the TF-IDF value in the document vector based on the query vector index and IDF
                query_index = query.split().index(token)
                tfidf = tf * idf_dict[token]
                doc_vectors[doc_id][query_index] = tfidf

    return doc_vectors

#compute cosine_similarity and return dictionary of {docid:cosine_similarity},already sorted, can make changes for like top 10
def create_cs_doc(query_vector,doc_vectors):
    doc_similarities={}
    for docid,vetcor in doc_vectors.items():
        doc_similarities[docid]=calculate_cosine_similarity(query_vector,vetcor)
    doc_similarities = {k: v for k, v in sorted(doc_similarities.items(), key=lambda item: item[1], reverse=True)}
    return doc_similarities



DOC1 = "the quick brown fox jumped over the lazy dog"
DOC2 = "dog 1 and dog 2 ate the hot dog"
DOC3 = "fox dog and"
#Q= "fox dog "
Q="fox dog and"
N=500 #total docs
df_fox=50#df of fox
df_dog=200#df of dog
df_and=400#df of and
idf_dict = {"fox":calculate_idf(N, df_fox),"dog":calculate_idf(N, df_dog),"and":calculate_idf(N, df_and)}#idf of each word

inverted_index_tfs = {"fox":{"doc1":(1/9),"doc2":0,"doc3":1/3},"dog":{"doc1":(1/9),"doc2":(1/3),"doc3":1/3},"and":{"doc1":(0/9),"doc2":(1/9),"doc3":1/3}}#tf of each word in different docs

query_vector=create_query_vector(Q,idf_dict)
doc_vectors=create_doc_vector(Q, query_vector, inverted_index_tfs, idf_dict)
cs=create_cs_doc(query_vector,doc_vectors)
#RESULT:{'doc3': 0.8729249902928188, 'doc1': 0.6923695754433984, 'doc2': 0.26863855424377914} the reason that score of the doc3 is not 1 becuase I add 0.1 to each for avoiding divide 0 errors
print(cs)


    
    






    
