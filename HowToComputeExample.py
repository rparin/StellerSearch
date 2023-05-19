import math

DOC1 = "the quick brown fox jumped over the lazy dog"
DOC2 = "dog 1 and dog 2 ate the hot dog"
Q= "fox dog"
N=500 #total docs

df_fox=50#df of each token in query
df_dog=200

# compute idf of a token  *idfs are the same for the same token, only depend on the df and N in docs
def calculate_idf(N, df):
    idf = math.log((N + 0.1) / (df + 0.1))
    return idf

# compute cosine_similarity bewteen query vector and doc vector, the vector lenth is 2, for deomo query "fox dog"
def calculate_cosine_similarity_demo(v1,v2):
    dot_product=v1[0]*v2[0]+v1[1]*v2[1]
    self_dot1= (v1[0]**2)+(v1[1]**2)
    self_dot2= (v2[0]**2)+(v2[1]**2)
    return dot_product/((math.sqrt(self_dot1*self_dot2))+0.1)

idf_fox=(calculate_idf(N, df_fox))
idf_dog = (calculate_idf(N, df_dog))


tf_idf_fox = (1/2)*idf_fox
tf_idf_dog=(1/2)*idf_dog


tf_idf_fox_doc1= (1/9)*idf_fox
tf_idf_dog_doc1=(1/9)*idf_dog


tf_idf_fox_doc2= (0/9)*idf_fox
tf_idf_dog_doc2=(3/9)*idf_dog

vector_query=[tf_idf_fox,tf_idf_dog]
vector_doc1= [tf_idf_fox_doc1,tf_idf_dog_doc1]
vector_doc2= [tf_idf_fox_doc2,tf_idf_dog_doc2]
print(vector_doc1,vector_doc2)

cosine_similarity1=calculate_cosine_similarity_demo(vector_query,vector_doc1)
cosine_similarity2=calculate_cosine_similarity_demo(vector_query,vector_doc2)

print("Cosine Similarity1:", cosine_similarity1)

print("Cosine Similarity2:", cosine_similarity2)
