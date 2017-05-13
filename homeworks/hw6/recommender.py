import csv
from typing import List, Dict, Tuple
from pprint import pprint

import numpy
from sklearn.metrics.pairwise import cosine_similarity

numpy.set_printoptions(precision=2, linewidth=999)

SKIP_GENRES = ['(no genres listed)']
RATING_THRESHOLD = 2.5


class User:
    def __init__(self, user_id, genres_count):
        super().__init__()
        self.id = user_id
        self.genre_ratings = numpy.zeros(genres_count, dtype=int)  # Ratings of genres by the user, normalized to (0,1)
        self.ratings: Dict[int, float] = {}  # Star-rating of given movies
        self.movies_rated = set()

    def __repr__(self, *args, **kwargs):
        return "User[{}]: {}".format(self.id, self.genre_ratings)

    def print_genre_ratings(self, genre_id_to_str, sort_by_name=False):
        print("User {} ratings:".format(self.id))

        if not sort_by_name:
            genre_ratings: List[Tuple[str, float]] = [(genre_id_to_str[i], self.genre_ratings[i]) for i in
                                                      range(0, self.genre_ratings.size)]

            genre_ratings = sorted(genre_ratings, key=lambda rating: rating[1], reverse=True)
            for genre_rating in genre_ratings:
                if genre_rating[1] > 0:
                    print("  {}: {}".format(genre_rating[0], genre_rating[1]))
        else:
            for i in range(0, self.genre_ratings.size):
                if self.genre_ratings[i] > 0:
                    print("  {}: {}".format(genre_id_to_str[i], self.genre_ratings[i]))


class Movie:
    def __init__(self, movie_id, title, genres):
        super().__init__()
        self.id = movie_id
        self.title = title
        self.genres = genres
        self.genres_vector = None

    def populate_genres_vector(self, genres_str_to_int: Dict[str, int]):
        self.genres_vector = numpy.zeros(len(genres_str_to_int))
        for genre in self.genres:
            genre_id = genres_str_to_int[genre]
            self.genres_vector[genre_id] = 1

        self.genres_vector = self.genres_vector.reshape(1, -1)

    def __repr__(self, *args, **kwargs):
        return "{} ({},{})".format(self.title, self.id, self.genres)


class Recommender:
    def __init__(self, movies_csv, ratings_csv):
        super().__init__()

        self.movies_csv_fn = movies_csv
        self.ratings_csv_fn = ratings_csv

        # self.movies: Dict[Movie], self.genres_list: List[str] = self._read_movies()
        self.movies, self.genres_list = self._read_movies()
        self.genre_str_to_id = {genre: i for i, genre in enumerate(self.genres_list)}
        self.genre_id_to_str = {i: genre for i, genre in enumerate(self.genres_list)}
        for movie in self.movies.values():
            movie.populate_genres_vector(self.genre_str_to_id)

        self.users: Dict[int, User] = self._read_users()

    def print_movies_ratings(self):
        """ Print average ratings for all movies. """
        score_sums: Dict[int, List[float, int]] = {}
        for user in self.users.values():
            for movie_id, rating in user.ratings.items():
                if movie_id not in score_sums:
                    score_sums[movie_id] = [0, 0]

                score_sums[movie_id][0] += user.ratings[movie_id]
                score_sums[movie_id][1] += 1

        for movie_id, (score_sum, users_count) in score_sums.items():
            print(f"{self.movies[movie_id].title:{100}.{50}} ({movie_id:{6}}): {score_sum/users_count:{6}.{4}}")

    def print_user_genre_ratings(self, user_id):
        """ Print summary of which genre was ranked how many times by the user. """
        self.users[user_id].print_genre_ratings(self.genre_id_to_str)

    def print_recommended_movies(self, recommended_movies):
        """ Pretty-print list of recommendations. """
        width_order = 2
        width_title = 50
        width_movid = 8
        width_score = 4
        precs_score = 4
        movtitle = "Movie title"
        movid = "Movie ID"
        movscore = "Score"

        print('-' * 80)
        print(f"    {movtitle:{width_title}} | {movid:{width_movid}} | {movscore:{width_score+precs_score+1}}")
        print('-' * 80)
        for i, (movie_id, score) in enumerate(recommended_movies):
            print(f"{i+1:{width_order}}. {self.movies[movie_id].title:{width_title}.{width_title}} | "
                  f"{movie_id:{width_movid}} | {score:{width_score}.{precs_score}}")
        print('-' * 80)

    def recommend_hybrid_based(self, user_id, limit_results: int, content_based_weight: float = 0.3,
                               collab_based_weight: float = 0.7, collab_use_top_n_similar_users: int = 20):
        content_recommendations = self.recommend_content_based(user_id)
        collab_recommendations = self.recommend_collaborative_based(
            user_id,
            use_top_n_similar_users=collab_use_top_n_similar_users)

        final_recommendations: Dict[int, float] = {mov_id: (score * content_based_weight) for mov_id, score
                                                   in content_recommendations}

        for mov_id, score in collab_recommendations:
            if mov_id not in final_recommendations:
                final_recommendations[mov_id] = 0
            final_recommendations[mov_id] += score

        sorted_final = sorted(final_recommendations.items(), key=lambda item: item[1], reverse=True)
        if limit_results > 0:
            return sorted_final[:limit_results]
        else:
            return sorted_final

    def recommend_content_based(self, user_id: int, limit_results: int = -1) -> List[Tuple[int, float]]:
        """
        Recommend top N results with Content-based recommending approach.

        Calculate cosine similarity of the given User's ratings to all movies in the Recommender (similarity
        of rated genres).
        E.g. if user
        :param user_id: ID of the user
        :param limit_results: Number of top results to return.
        :return: List of (movie_id, similarity) tuples sorted in descending order based on similarity.
        """
        similarities: Dict[int, float] = {}

        non_rated_movies = [movie for movie in self.movies.values() if movie.id not in self.users[user_id].movies_rated]
        for movie in non_rated_movies:
            similarity = cosine_similarity(self.users[user_id].genre_ratings.reshape(1, -1), movie.genres_vector)[0][0]
            similarities[movie.id] = similarity

        # Sort obtained similarities, best first
        sorted_similarities: List[Tuple[int, float]] = sorted(similarities.items(),
                                                              key=lambda item: item[1],
                                                              reverse=True)
        if limit_results > 0:
            return sorted_similarities[:limit_results]
        else:
            return sorted_similarities

    def recommend_collaborative_based(self, user_id: int, limit_results: int = -1, use_top_n_similar_users: int = 5) -> \
            List[Tuple[int, float]]:
        """
        Recommend top N results with Collaborative filtering approach.

        - Calculate cosine similarity of the given user's rating vector to all other users.
        - Select the best N matches
        - Build a new movie rating vector as a weighted mean of all the ratings the other users made.
        - Sort the ratings descendingly, recommend the movies with the highest ranking that the user has not seen yet
        :param user_id:
        :param limit_results
        :param use_top_n_similar_users:
        :return:
        """
        this_user = self.users[user_id]

        similarities: Dict[int, float] = {}
        for user in self.users.values():
            if user_id == user.id:
                continue  # skip this user

            similarity = \
                cosine_similarity(this_user.genre_ratings.reshape(1, -1), user.genre_ratings.reshape(1, -1))[0][0]
            similarities[user.id] = similarity

        # Sort obtained similarities, best first
        sorted_similar_users: List[Tuple[int, float]] = sorted(similarities.items(),
                                                               key=lambda item: item[1],
                                                               reverse=True)[:use_top_n_similar_users]

        print("*" * 80)
        print("Using similar users:")
        pprint(sorted_similar_users)
        print("*" * 80)
        # Build a new movie rating from similar users
        # ranking = (A_ranking * A_weight + B_ranking*B_weight +... ) / len(users)
        temp_ratings: Dict[int, List[float, int]] = {}  # Dict of {movie_id: (sum_ratings, count_people)}
        for user, user_similarity in [(self.users[user_id], _user_similarity)
                                      for user_id, _user_similarity in
                                      sorted_similar_users]:  # Iterate through User objects and their similarities
            for movie_id, movie_rating in user.ratings.items():  # Iterate through the Users' ratings
                if movie_id in this_user.movies_rated:  # Skip movies that the user has already rated
                    continue

                if movie_id not in temp_ratings:
                    temp_ratings[movie_id] = [0, 0]

                temp_ratings[movie_id][0] += movie_rating * user_similarity  # Add weighed sum to the total movie rating
                temp_ratings[movie_id][1] += 1

        # Calculate weighed average from the dictionary constructed above, just divide the values
        new_ratings: Dict[int, float] = {movie_id: temp_rating[0] / temp_rating[1]
                                         for movie_id, temp_rating in temp_ratings.items()}
        sorted_new_ratings: Dict[int, float] = sorted(new_ratings.items(), key=lambda rating: rating[1], reverse=True)

        # Normalize ratings to be in interval (0,1)
        max_val = sorted_new_ratings[0][1]
        normalized_sorted_new_ratings = [(rating[0], (rating[1] / max_val)) for rating in sorted_new_ratings]

        if limit_results > 0:
            return normalized_sorted_new_ratings[:limit_results]
        else:
            return normalized_sorted_new_ratings

    def _read_movies(self) -> Tuple[Dict[int, Movie], List[str]]:
        """
        Read datafile with movies.
        :return: Tuple: (
                         dict of Movie objects (key = movie_id),
                         list of genres (as strings)
                        )
        """

        genres_set = set()
        movies = {}

        with open(self.movies_csv_fn, encoding="utf-8") as f:
            f.readline()
            f.readline()
            reader = csv.reader(f, delimiter=',')
            for movie_row in reader:
                # print("Row: {}".format(movie_row))
                movie_id = int(movie_row[0])
                title = movie_row[1]
                genres = [genre.strip() for genre in movie_row[2].split('|') if genre.strip() not in SKIP_GENRES]
                movie = Movie(movie_id, title, genres)
                movies[movie_id] = movie
                genres_set = genres_set.union(set(genres))

        return movies, sorted(list(genres_set))

    def _read_users(self) -> Dict[int, User]:
        users: Dict[int, User] = {}

        with open(self.ratings_csv_fn, encoding="utf-8") as f:
            f.readline()
            f.readline()
            reader = csv.reader(f, delimiter=',', )
            for i, rating_row in enumerate(reader):
                user_id = int(rating_row[0])
                movie_id = int(rating_row[1])
                rating = float(rating_row[2])
                if user_id not in users:
                    users[user_id] = User(user_id, len(self.genre_str_to_id))

                users[user_id].movies_rated.add(movie_id)
                users[user_id].ratings[movie_id] = rating
                for movie_genre in self.movies[movie_id].genres:
                    if rating >= RATING_THRESHOLD:
                        users[user_id].genre_ratings[self.genre_str_to_id[movie_genre]] += 1

        # TODO Not sure about this - normalizing user rating vector to have scores in (0,1).
        # Reason - Vector (3,1,0) would be closer to (0,1,0) than (3,0,0), but user clearly more prefers the first genre
        for user in users.values():
            user.genre_ratings = user.genre_ratings / numpy.amax(user.genre_ratings)

        return users


def main():
    recommender = Recommender('data/movies.csv', 'data/ratings.csv')

    user_id = 1
    recommendation_count = 10

    recommender.print_movies_ratings()
    recommender.print_user_genre_ratings(user_id)

    hybrid_recommended = recommender.recommend_hybrid_based(user_id, recommendation_count)
    recommender.print_recommended_movies(hybrid_recommended)


if __name__ == '__main__':
    main()
