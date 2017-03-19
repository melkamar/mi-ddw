# import
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

# prepare corpus
corpus = []
for d in range(1400):
    f = open("./d/"+str(d+1)+".txt")
    corpus.append(f.read())

# add query to corpus
for q in [1]:
    f = open("./q/"+str(q)+".txt")
    corpus.append(f.read())

# init vectorizer
tfidf_vectorizer = TfidfVectorizer()

# prepare matrix
tfidf_matrix = tfidf_vectorizer.fit_transform(corpus)

# compute similarity between query and all docs (tf-idf) and get top 10 relevant
sim = np.array(cosine_similarity(tfidf_matrix[len(corpus)-1], tfidf_matrix[0:(len(corpus)-1)])[0])
topRelevant = sim.argsort()[-10:][::-1]+1
print(topRelevant)