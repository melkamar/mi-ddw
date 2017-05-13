import csv
import numpy

SKIP_GENRES = ['(no genres listed)']
RATING_THRESHOLD = 2.5


class Recommender:
    def __init__(self, movies_csv, ratings_csv):
        super().__init__()

        self.movies_csv_fn = movies_csv
        self.ratings_csv_fn = ratings_csv

        self.movies, self.genres_list = self.read_movies()
        self.genre_str_to_id = {genre: i for i, genre in enumerate(self.genres_list)}
        self.genre_id_to_str = {i: genre for i, genre in enumerate(self.genres_list)}

        self.users = self.read_users()

        # pprint(genre_str_to_id)
        for user in self.users.values():
            user.print_genre_ratings(self.genre_id_to_str)

    def read_movies(self):
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

    def read_users(self):
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

                for movie_genre in self.movies[movie_id].genres:
                    if rating >= RATING_THRESHOLD:
                        users[user_id].ratings[self.genre_str_to_id[movie_genre]] += 1

        return users


class User:
    def __init__(self, user_id, genres_count):
        super().__init__()
        self.id = user_id
        self.ratings = numpy.zeros(genres_count, dtype=int)

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


if __name__ == '__main__':
    main()
