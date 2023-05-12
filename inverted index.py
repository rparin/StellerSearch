import os
import re
import collections
from nltk.stem import PorterStemmer
import json

#inverted_index = defaultdict(list)
inverted_index = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(list)))

stemmer = PorterStemmer()
def preprocess_text(text):
   text = text.lower()
   text = re.sub('<[^<]+?>', '', text)
   tokens = re.findall(r'\b\w+\b', text)
   tokens = [stemmer.stem(token) for token in tokens]
   return tokens


def build_inverted_index(directory):
    file_num =0 
    doc_ids = {}
    file_path = os.path.join(directory, "doc_ids.json")
    if os.path.exists(file_path):
        os.remove(file_path)
    #tag_weights = {'title': 3, 'h1': 2.5, 'h2': 2, 'h3': 1.5, 'b': 1, 'strong': 1} #tags' weight
    for subdir, dirs, files in os.walk(directory):
        for file in files:
            path = subdir.replace("\\", "//")
            if file.endswith('.json'):
                try:
                    with open(os.path.join(path, file).replace("\\", "//"), 'r', encoding="utf-8") as f:
                            data = json.load(f)
                    file_num += 1
                    doc_id = data['url']
                    fileName="doc"+str(file_num)
                    doc_ids[fileName] = doc_id
                    doc_content = data['content']
                    tokens = preprocess_text(doc_content)
                    #redefine
                    tokens_withtags = preprocess_text(doc_content)
                    
                    #positions = defaultdict(lambda: {"1": [],"1.33": [], "1.66": [],"2": []})
                    #tag postion
                    #tag_positions = collections.defaultdict(lambda: collections.defaultdict(list))
                    #for tag in tag_weights.keys():
                        #tag_regex = fr'<{tag}.*?>(.*?)<\/{tag}>'
                        #matches = re.findall(tag_regex, tokens_withtags, flags=re.IGNORECASE)
                        #for match in matches:
                            #start_index = match.start()
                            #end_index = match.end()
                            #tag_positions[tag].append((start_index, end_index))

                    #token postion
                    for i, token in enumerate(tokens_withtags):
                        if token in tokens:
                            count=0
                            #for k,v in tag_positions.items():
                                #for start,end in v:
                                    #if start <= i <= end:
                                        #if count==0: 
                                            #inverted_index[token][doc_id][k].append(i)
                                            #count+=1
                            if count==0:
                                inverted_index[token][fileName]["normal"].append(i)
                                #inverted_index[token][doc_id]["normal"].append(i)
                                count+=1
                    
                    #use this for enumerate dict built by Ralph
                    #dict_token_tags_pair= tokonizer();
                    #for token in dict_token_tags_pair.keys():
                        #for tags in token.keys():
                            #inverted_index[token][fileName][tags]=token[tags]
                    
                except :
                    continue
 
        
    #idf = {}
    #for token, posting in inverted_index.items():
        #idf[token] = math.log((file_num + 0.1) / (0.1+ len(posting)))+0.1
        #for i in range(len(posting)):
            #posting[i][2] = posting[i][2] * (idf[token])
    #print file number
    print("total file: "+str(file_num))
    #write doc id and url pair to local json
    with open(file_path, "w") as f:
        json.dump(doc_ids, f)
    
    return inverted_index


def load_index(url):
    with open(url, 'r') as f:
        return json.load(f)
def main():
    while True:
        choice = input("Do you have the inverted index file already? (y/n/q)")
        if choice.lower() == "y":
            filename = input("Please enter the file address: ")
            try:
                with open(filename, "r") as f:
                    inverted_index = eval(f.read())
                    break
            except (FileNotFoundError, SyntaxError):
                print("Invalid file address. Please try again.")
        elif choice.lower() == "n":
            directory = input("Please enter the directory where the html files at and save the inverted index file: ")
            try:
                os.makedirs(directory, exist_ok=True)
                filename = os.path.join(directory, "inverted_index.txt")
                inverted_index = build_inverted_index(directory)
                print(len(set(inverted_index.keys())))
                with open(filename, "w") as f:
                    json.dump(inverted_index, f, indent=2)
                break
            except OSError:
                print("Invalid directory. Please try again.")
        elif choice.lower() == "q":
            exit()
if __name__ == '__main__':
    main()
