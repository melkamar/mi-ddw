from collections import namedtuple
import numpy as np
import scipy.sparse
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances

data = []
RELEVANT_DOCUMENT_COUNT = 150

Weighting_Result = namedtuple("Weighting_Result", ["euclidean", "cosine"])


def get_data():
    """ Return list of strings, each string is one document. """
    # return data if data else ['this is a sample string',
    #                           'second string is like the first',
    #                           "the the the xoxoxo"]
    return data if data else [open("./data/d/" + str(d + 1) + ".txt").read() for d in range(1400)]


def get_queries():
    """ Return list of strings, each string is a query. """
    # return ['the string is a']
    return [open("./data/q/" + str(q) + ".txt").read() for q in range(1, 226)]


def get_relevant_docs(query_id):
    """ Return list of numbers denoting documents relevant to the given query. """
    res = []
    with open("./data/r/{}.txt".format(query_id)) as f:
        for line in f.readlines():
            res.append(int(line))

    return res


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

    euclid_distances = calculate_distances_euclidean(query_vector, data_vectors)
    cosine_similarities = calculate_cosine_similarity(query_vector, data_vectors)
    print("Binary Euclid: {}".format(euclid_distances))
    print("Binary Cosine: {}".format(cosine_similarities))

    return Weighting_Result(euclidean=euclid_distances, cosine=cosine_similarities)


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

    euclid_distances = calculate_distances_euclidean(query_vector, data_vectors)
    cosine_similarities = calculate_cosine_similarity(query_vector, data_vectors)
    print("TF Euclid: {}".format(euclid_distances))
    print("TF Cosine: {}".format(cosine_similarities))

    return Weighting_Result(euclidean=euclid_distances, cosine=cosine_similarities)


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

    euclid_distances = calculate_distances_euclidean(query_vector, data_vectors)
    cosine_similarities = calculate_cosine_similarity(query_vector, data_vectors)
    print("TF-IDF Euclid: {}".format(euclid_distances))
    print("TF-IDF Cosine: {}".format(cosine_similarities))

    return Weighting_Result(euclidean=euclid_distances, cosine=cosine_similarities)


def calculate_precision(retrieved_documents, relevant_documents):
    relevant_count = 0
    for doc in retrieved_documents:
        if doc in relevant_documents:
            relevant_count += 1

    return relevant_count / len(retrieved_documents)


def calculate_recall(retrieved_documents, relevant_documents):
    relevant_count = 0
    for doc in retrieved_documents:
        if doc in relevant_documents:
            relevant_count += 1

    return relevant_count / len(relevant_documents)


Query_Results = namedtuple("Query_Results", ["binary_precision",
                                             "binary_recall",
                                             "tf_precision",
                                             "tf_recall",
                                             "tfidf_precision",
                                             "tfidf_recall",
                                             ])


def process_queries():
    euclidean_results = []
    cosine_results = []

    queries = get_queries()
    for i, query in enumerate(queries, 1):
        binary_result = process_query_binary(query)
        tf_result = process_query_term_frequency(query)
        tfidf_result = process_query_tfidf(query)

        relevant_docs = get_relevant_docs(i)

        print("Got:      {}".format(binary_result))
        print("Expected: {}".format(relevant_docs))

        euclidean_results.append(Query_Results(
            binary_precision=calculate_precision(binary_result.euclidean[:len(relevant_docs)], relevant_docs),
            binary_recall=calculate_recall(binary_result.euclidean[:len(relevant_docs)], relevant_docs),
            tf_precision=calculate_precision(tf_result.euclidean[:len(relevant_docs)], relevant_docs),
            tf_recall=calculate_recall(tf_result.euclidean[:len(relevant_docs)], relevant_docs),
            tfidf_precision=calculate_precision(tfidf_result.euclidean[:len(relevant_docs)], relevant_docs),
            tfidf_recall=calculate_recall(tfidf_result.euclidean[:len(relevant_docs)], relevant_docs)
        ))

        cosine_results.append(Query_Results(
            binary_precision=calculate_precision(binary_result.cosine[:len(relevant_docs)], relevant_docs),
            binary_recall=calculate_recall(binary_result.cosine[:len(relevant_docs)], relevant_docs),
            tf_precision=calculate_precision(tf_result.cosine[:len(relevant_docs)], relevant_docs),
            tf_recall=calculate_recall(tf_result.cosine[:len(relevant_docs)], relevant_docs),
            tfidf_precision=calculate_precision(tfidf_result.cosine[:len(relevant_docs)], relevant_docs),
            tfidf_recall=calculate_recall(tfidf_result.cosine[:len(relevant_docs)], relevant_docs)
        ))


    binary_euclidean_precision_sum = 0
    binary_cosine_precision_sum = 0
    binary_euclidean_recall_sum = 0
    binary_cosine_recall_sum = 0
    tf_euclidean_precision_sum = 0
    tf_cosine_precision_sum = 0
    tf_euclidean_recall_sum = 0
    tf_cosine_recall_sum = 0
    tfidf_euclidean_precision_sum = 0
    tfidf_cosine_precision_sum = 0
    tfidf_euclidean_recall_sum = 0
    tfidf_cosine_recall_sum = 0

    for i, query in enumerate(queries, 1):
        binary_euclidean_precision = euclidean_results[i - 1].binary_precision
        binary_cosine_precision = cosine_results[i - 1].binary_precision
        binary_euclidean_recall = euclidean_results[i - 1].binary_recall
        binary_cosine_recall = cosine_results[i - 1].binary_recall
        tf_euclidean_precision = euclidean_results[i - 1].tf_precision
        tf_cosine_precision = cosine_results[i - 1].tf_precision
        tf_euclidean_recall = euclidean_results[i - 1].tf_recall
        tf_cosine_recall = cosine_results[i - 1].tf_recall
        tfidf_euclidean_precision = euclidean_results[i - 1].tfidf_precision
        tfidf_cosine_precision = cosine_results[i - 1].tfidf_precision
        tfidf_euclidean_recall = euclidean_results[i - 1].tfidf_recall
        tfidf_cosine_recall = cosine_results[i - 1].tfidf_recall

        binary_euclidean_precision_sum +=binary_euclidean_precision
        binary_cosine_precision_sum += binary_cosine_precision
        binary_euclidean_recall_sum +=binary_euclidean_recall
        binary_cosine_recall_sum +=binary_cosine_recall
        tf_euclidean_precision_sum +=tf_euclidean_precision
        tf_cosine_precision_sum += tf_cosine_precision
        tf_euclidean_recall_sum +=tf_euclidean_recall
        tf_cosine_recall_sum +=tf_cosine_recall
        tfidf_euclidean_precision_sum +=tfidf_euclidean_precision
        tfidf_cosine_precision_sum += tfidf_cosine_precision
        tfidf_euclidean_recall_sum +=tfidf_euclidean_recall
        tfidf_cosine_recall_sum +=tfidf_cosine_recall

        print(
            """
            Query #{query_num}
            -------------------------------------
            Binary
                - Precision:
                    - Euclidean: {binary_euclidean_precision}
                    - Cosine: {binary_cosine_precision}
                - Recall:
                    - Euclidean: {binary_euclidean_recall}
                    - Cosine: {binary_cosine_recall}

            Term frequency
                - Precision:
                    - Euclidean: {tf_euclidean_precision}
                    - Cosine: {tf_cosine_precision}
                - Recall:
                    - Euclidean: {tf_euclidean_recall}
                    - Cosine: {tf_cosine_recall}

            TF-IDF
                - Precision:
                    - Euclidean: {tfidf_euclidean_precision}
                    - Cosine: {tfidf_cosine_precision}
                - Recall:
                    - Euclidean: {tfidf_euclidean_recall}
                    - Cosine: {tfidf_cosine_recall}
            """.format(
                query_num=i,
                binary_euclidean_precision=binary_euclidean_precision,
                binary_cosine_precision=binary_cosine_precision,
                binary_euclidean_recall=binary_euclidean_recall,
                binary_cosine_recall=binary_cosine_recall,
                tf_euclidean_precision=tf_euclidean_precision,
                tf_cosine_precision=tf_cosine_precision,
                tf_euclidean_recall=tf_euclidean_recall,
                tf_cosine_recall=tf_cosine_recall,
                tfidf_euclidean_precision=tfidf_euclidean_precision,
                tfidf_cosine_precision=tfidf_cosine_precision,
                tfidf_euclidean_recall=tfidf_euclidean_recall,
                tfidf_cosine_recall=tfidf_cosine_recall,

            )
        )


    print(
        """
        -------------------------------------
        AVERAGE
        -------------------------------------
        Binary
            - Precision:
                - Euclidean: {binary_euclidean_precision}
                - Cosine: {binary_cosine_precision}
            - Recall:
                - Euclidean: {binary_euclidean_recall}
                - Cosine: {binary_cosine_recall}

        Term frequency
            - Precision:
                - Euclidean: {tf_euclidean_precision}
                - Cosine: {tf_cosine_precision}
            - Recall:
                - Euclidean: {tf_euclidean_recall}
                - Cosine: {tf_cosine_recall}

        TF-IDF
            - Precision:
                - Euclidean: {tfidf_euclidean_precision}
                - Cosine: {tfidf_cosine_precision}
            - Recall:
                - Euclidean: {tfidf_euclidean_recall}
                - Cosine: {tfidf_cosine_recall}
        """.format(
            binary_euclidean_precision=binary_euclidean_precision_sum / len(queries),
            binary_cosine_precision=binary_cosine_precision_sum / len(queries),
            binary_euclidean_recall=binary_euclidean_recall_sum / len(queries),
            binary_cosine_recall=binary_cosine_recall_sum / len(queries),
            tf_euclidean_precision=tf_euclidean_precision_sum / len(queries),
            tf_cosine_precision=tf_cosine_precision_sum / len(queries),
            tf_euclidean_recall=tf_euclidean_recall_sum / len(queries),
            tf_cosine_recall=tf_cosine_recall_sum / len(queries),
            tfidf_euclidean_precision=tfidf_euclidean_precision_sum / len(queries),
            tfidf_cosine_precision=tfidf_cosine_precision_sum / len(queries),
            tfidf_euclidean_recall=tfidf_euclidean_recall_sum / len(queries),
            tfidf_cosine_recall=tfidf_cosine_recall_sum / len(queries),

        )
    )

process_queries()
