# import
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
import numpy as np
import scipy.sparse
from pprint import pprint

data = []

RELEVANT_DOCUMENT_COUNT = 10

def get_data():
    """ Return list of strings, each string is one document. """
    return data if data else ['this is a sample string',
                              'second string is like the first',
                              "the the the xoxoxo"]
    # return data if data else [open("./data/d/" + str(d + 1) + ".txt").read() for d in range(1400)]


def get_queries():
    """ Return list of strings, each string is a query. """
    return ['the string is a']
    # return [open("./data/q/" + str(q) + ".txt").read() for q in [1]]


def get_relevant_docs(query_id):
    """ Return list of numbers denoting documents relevant to the given query. """
    with open("./r/{}".format(query_id)) as f:
        return f.readlines()


def calculate_distances_euclidean(query_vector, data_vectors):
    """
    Calculate distances of query_vector from all of data_vectors using Euclidean distance.
    Return sorted indices based on the distance.

    Args:
        query_vector: A single vector of numbers defining the query.
        data_vectors: List of vectors defining the documents being worked at.

    Returns:
        List of indices into data_vectors, sorted by the distance. Closest first.
    """
    distances = np.array(
        euclidean_distances(query_vector, data_vectors)[0])  # result is [[ data ]], so get idx 0 to have [ data ]

    distances_sorted = distances.argsort() + 1  # argsort will return a sorted list of indices of the original data (+1 because documents are indexed from 1)
    return distances_sorted


def calculate_cosine_similarity(query_vector, data_vectors):
    """
    Calculate distances of query_vector from all of data_vectors using Cosine similarity metric.
    Return sorted indices based on the distance.

    Args:
        query_vector: A single vector of numbers defining the query.
        data_vectors: List of vectors defining the documents being worked at.

    Returns:
        List of indices into data_vectors, sorted by the similarity. Most similar first.
    """
    distances = np.array(
        cosine_similarity(query_vector, data_vectors)[0])  # result is [[ data ]], so get idx 0 to have [ data ]

    # argsort will return a sorted list of indices of the original data (+1 because documents are indexed from 1)
    # for cosine similarity, higher is better, so invert the list by [::-1]
    distances_sorted = distances.argsort()[::-1] + 1
    return distances_sorted


def process_query_binary(query):
    data = list(get_data())
    data.append(query)

    vectorizer = CountVectorizer(binary=True)
    count_array = vectorizer.fit_transform(data)

    # print(vectorizer.get_feature_names())
    # print(count_array.toarray())

    query_vector = count_array[len(data) - 1]  # last row is the query
    data_vectors = count_array[0:len(data) - 1]  # anything but last row is data
    # print("Query vector: {}".format(query_vector.toarray()))
    # print("Data vectors: {}".format(data_vectors.toarray()))

    euclid_distances = calculate_distances_euclidean(query_vector, data_vectors)[:RELEVANT_DOCUMENT_COUNT]
    cosine_similarities = calculate_cosine_similarity(query_vector, data_vectors)[:RELEVANT_DOCUMENT_COUNT]
    print("Binary Euclid: {}".format(euclid_distances))
    print("Binary Cosine: {}".format(cosine_similarities))


def process_query_term_frequency(query):
    data = list(get_data())
    data.append(query)

    vectorizer = CountVectorizer()
    count_array = vectorizer.fit_transform(data)

    sums = count_array.sum(1)  # Sum over rows (arg 1), produce a vector.
    normalized_array = count_array.multiply(1 / sums)  # Normalize all rows - divide each row by its sum.

    # Convert to csr_matrix (multiplication kept returning other type and that threw errors ¯\_(ツ)_/¯
    normalized_array = scipy.sparse.csr_matrix(normalized_array)

    # print(np.array2string(normalized_array.toarray(), max_line_width=800))

    query_vector = normalized_array[len(data) - 1]  # last row is the query
    data_vectors = normalized_array[0:len(data) - 1]  # anything but last row is data

    # print("Query vector: {}".format(query_vector.toarray()))
    # print("Data vectors: {}".format(data_vectors.toarray()))

    euclid_distances = calculate_distances_euclidean(query_vector, data_vectors)[:RELEVANT_DOCUMENT_COUNT]
    cosine_similarities = calculate_cosine_similarity(query_vector, data_vectors)[:RELEVANT_DOCUMENT_COUNT]
    print("TF Euclid: {}".format(euclid_distances))
    print("TF Cosine: {}".format(cosine_similarities))


def process_query_tfidf(query):
    data = list(get_data())
    data.append(query)

    tfidf_vectorizer = TfidfVectorizer()

    # prepare matrix
    tfidf_matrix = tfidf_vectorizer.fit_transform(data)

    # compute similarity between query and all docs (tf-idf) and get top 10 relevant
    query_vector = tfidf_matrix[len(data) - 1]  # last row is the query
    data_vectors = tfidf_matrix[0:len(data) - 1]  # anything but last row is data
    # print("Query vector: {}".format(query_vector.toarray()))
    # print("Data vectors: {}".format(data_vectors.toarray()))

    euclid_distances = calculate_distances_euclidean(query_vector, data_vectors)[:RELEVANT_DOCUMENT_COUNT]
    cosine_similarities = calculate_cosine_similarity(query_vector, data_vectors)[:RELEVANT_DOCUMENT_COUNT]
    print("TF-IDF Euclid: {}".format(euclid_distances))
    print("TF-IDF Cosine: {}".format(cosine_similarities))


def process_queries():
    queries = get_queries()
    for query in queries:
        process_query_binary(query)
        process_query_term_frequency(query)
        process_query_tfidf(query)


process_queries()
