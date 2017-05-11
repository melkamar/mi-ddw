from math import sqrt
from numpy import genfromtxt
import numpy
from sklearn.metrics.pairwise import cosine_similarity
import csv


class UserRating:
    def __init__(self, name, ratings):
        super().__init__()
        self.name = name
        self.ratings = numpy.array(ratings.reshape(1, -1), dtype=float)

    def __str__(self, *args, **kwargs):
        return f"User({self.name})"

    def __repr__(self, *args, **kwargs):
        return f"User({self.name})"


def loadData(fn):
    data = []

    with open(fn) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            data.append(UserRating(row[0], numpy.array(row[1:])))

    return data


def user_sim_cosine_sim(person1, person2):
    numerator = 0
    denom_1 = 0
    denom_2 = 0
    for i in range(0, person1.ratings.size):
        if person1.ratings[0][i] == 0 or person2.ratings[0][i] == 0:
            continue
        else:
            numerator += person1.ratings[0][i] * person2.ratings[0][i]
            denom_1 += person1.ratings[0][i] ** 2
            denom_2 += person2.ratings[0][i] ** 2

    denominator = sqrt(denom_1) * sqrt(denom_2)

    similarity = numerator / denominator
    print(f"Similarity between {person1.name} and {person2.name}: {similarity}")
    return similarity


def user_sim_pearson_corr(person1, person2):
    numerator = 0
    denom_1 = 0
    denom_2 = 0
    mean_1 = 0
    mean_2 = 0

    # calculate mean
    items = 0
    for i in range(0, person1.ratings.size):
        if person1.ratings[0][i] == 0 or person2.ratings[0][i] == 0:
            continue
        else:
            mean_1 += person1.ratings[0][i]
            mean_2 += person2.ratings[0][i]
            items += 1

    mean_1 /= items
    mean_2 /= items

    for i in range(0, person1.ratings.size):
        if person1.ratings[0][i] == 0 or person2.ratings[0][i] == 0:
            continue
        else:
            numerator += (person1.ratings[0][i] - mean_1) * (person2.ratings[0][i] - mean_2)
            denom_1 += (person1.ratings[0][i] - mean_1) ** 2
            denom_2 += (person2.ratings[0][i] - mean_2) ** 2

    denominator = sqrt(denom_1) * sqrt(denom_2)
    similarity = numerator / denominator
    print(f"Pearson coefficient between {person1.name} and {person2.name}: {similarity}")
    return similarity


# computes similarity between two users based on the pearson similarity metric

def most_similar_users(person, number_of_users, other_users):
    similarities = {}
    for other_user in other_users:
        #similarity = user_sim_cosine_sim(person, other_user)
        similarity = user_sim_pearson_corr(person, other_user)
        similarities[other_user] = similarity

    sorted_similarities = sorted(similarities.items(), key=lambda user: user[1], reverse=True)
    print(sorted_similarities)
    return sorted_similarities[:number_of_users]


def user_recommendations(person, other_persons, use_k_users=2):
    top_similar_users = most_similar_users(person, use_k_users, other_persons)
    missing_items_indices = []
    for index in range(0, person.ratings.size):
        if person.ratings[0][index] == 0:
            missing_items_indices.append(index)

    print(f"Need to recommend items: {missing_items_indices}")

    item_scores = {}
    for item_index in missing_items_indices:
        item_score = 0
        for similar_user in top_similar_users:
            item_score += similar_user[0].ratings[0][item_index]

        item_score /= len(top_similar_users)  # Make average of other users' ratings to a movie
        item_scores[item_index] = item_score

    # Sort obtained item scores
    sorted_scores = sorted(item_scores.items(), key=lambda item: item[1], reverse=True)
    print(f"Sorted recommendation scores (movie_id, score): {sorted_scores}")


def main():
    data = loadData('small-dataset.csv')
    person1 = data[2]
    other_persons = data[:2] + data[3:]

    user_recommendations(person1, other_persons, use_k_users=2)


if __name__ == '__main__':
    main()
