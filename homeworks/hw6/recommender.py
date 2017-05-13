import csv
import numpy
from sklearn.metrics.pairwise import cosine_similarity

numpy.set_printoptions(precision=2, linewidth=999)

SKIP_GENRES = ['(no genres listed)']
RATING_THRESHOLD = 2.5


class Recommender:
    def __init__(self, movies_csv, ratings_csv):
        super().__init__()

        self.movies_csv_fn = movies_csv
        self.ratings_csv_fn = ratings_csv

        self.movies, self.genres_list = self._read_movies()
        self.genre_str_to_id = {genre: i for i, genre in enumerate(self.genres_list)}
        self.genre_id_to_str = {i: genre for i, genre in enumerate(self.genres_list)}

        self.users = self._read_users()

        # pprint(genre_str_to_id)
        for user in self.users.values():
            user.print_genre_ratings(self.genre_id_to_str)

    def recommend_content_based(self, user_id, top_n_results):
        """
        Calculate cosine similarity of the given User's ratings to all movies in the Recommender (similarity
        of rated genres). Returns the top N genre-similar movies.
        E.g. if user
        :param user_id: ID of the user
        :param top_n_results: Number of top results to return.
        :return:
        """
        for movie in self.movies:
            pass



    def _read_movies(self):
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
                movie_id = movie_row[0]
                title = movie_row[1]
                genres = [genre.strip() for genre in movie_row[2].split('|') if genre.strip() not in SKIP_GENRES]
                movie = Movie(movie_id, title, genres)
                movies[movie_id] = movie
                genres_set = genres_set.union(set(genres))

        return movies, sorted(list(genres_set))

    def _read_users(self):
        users = {}

        with open(self.ratings_csv_fn, encoding="utf-8") as f:
            f.readline()
            f.readline()
            reader = csv.reader(f, delimiter=',', )
            for i, rating_row in enumerate(reader):
                user_id = rating_row[0]
                movie_id = rating_row[1]
                rating = float(rating_row[2])
                if user_id not in users:
                    users[user_id] = User(user_id, len(self.genre_str_to_id))

                users[user_id].movies_rated.add(movie_id)
                for movie_genre in self.movies[movie_id].genres:
                    if rating >= RATING_THRESHOLD:
                        users[user_id].ratings[self.genre_str_to_id[movie_genre]] += 1

        # TODO Not sure about this - normalizing user rating vector to have scores in (0,1).
        # Reason - Vector (3,1,0) would be closer to (0,1,0) than (3,0,0), but user clearly more prefers the first genre
        for user in users.values():
            print("{} Pre-normalization: {}".format(user.id, user.ratings))
            user.ratings = user.ratings / numpy.amax(user.ratings)
            print("{} Post-normalization: {}".format(user.id, user.ratings))

        return users


class User:
    def __init__(self, user_id, genres_count):
        super().__init__()
        self.id = user_id
        self.ratings = numpy.zeros(genres_count, dtype=int)
        self.movies_rated = set()

    def __repr__(self, *args, **kwargs):
        return "User[{}]: {}".format(self.id, self.ratings)

    def print_genre_ratings(self, genre_id_to_str):
        print("User {} ratings:".format(self.id))
        for i in range(0, self.ratings.size):
            if self.ratings[i] > 0:
                print("  {}: {}".format(genre_id_to_str[i], self.ratings[i]))


class Movie:
    def __init__(self, movie_id, title, genres):
        super().__init__()
        self.id = movie_id
        self.title = title
        self.genres = genres

    def __repr__(self, *args, **kwargs):
        return "{} ({},{})".format(self.title, self.id, self.genres)


def main():
    recommender = Recommender('data/movies.csv', 'data/ratings.csv')
    recommender.recommend_content_based(1, 5)

if __name__ == '__main__':
    main()
