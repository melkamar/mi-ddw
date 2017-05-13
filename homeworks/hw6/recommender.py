from pprint import pprint
import csv
import numpy

SKIP_GENRES = ['(no genres listed)']
RATING_THRESHOLD = 2.5


class User:
    def __init__(self, user_id, genres_count):
        super().__init__()
        self.id = user_id
        self.ratings = numpy.zeros(genres_count)

    # def __repr__(self, *args, **kwargs):
    #     return "User[{}]: {}".format(self.id, self.ratings)

    def print_genre_ratings(self, genre_id_to_str):
        print("User {} ratings:".format(self.id))
        for i in range(0, self.ratings.size):
            print("  {}: {}".format(genre_id_to_str[i], self.ratings[i]))


class Movie:
    def __init__(self, movie_id, title, genres):
        super().__init__()
        self.id = movie_id
        self.title = title
        self.genres = genres

    def __repr__(self, *args, **kwargs):
        return "{} ({},{})".format(self.title, self.id, self.genres)


def read_movies(fn):
    """
    Read datafile with movies.
    :param fn:
    :return: Tuple: (
                     dict of Movie objects (key = movie_id),
                     list of genres (as strings)
                    )
    """

    genres_set = set()
    movies = {}

    with open(fn, encoding="utf-8") as f:
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


def read_users(fn, movies, genre_str_to_id):
    users = {}

    with open(fn, encoding="utf-8") as f:
        f.readline()
        f.readline()
        reader = csv.reader(f, delimiter=',', )
        for i, rating_row in enumerate(reader):
            if i > 1:
                break
            print("Row: {}".format(rating_row))
            user_id = rating_row[0]
            movie_id = rating_row[1]
            rating = float(rating_row[2])
            if user_id not in users:
                users[user_id] = User(user_id, len(genre_str_to_id))

            for movie_genre in movies[movie_id].genres:
                if rating >= RATING_THRESHOLD:
                    users[user_id].ratings[genre_str_to_id[movie_genre]] += 1

                    # genres = [genre.strip() for genre in rating_row[2].split('|') if genre.strip() not in SKIP_GENRES]
                    # movie = Movie(movie_id, title, genres)
                    # users[movie_id] = movie
                    # genres_set = genres_set.union(set(genres))

    return users


def main():
    movies, genres = read_movies('data/movies.csv')
    genre_str_to_id = {genre: i for i, genre in enumerate(genres)}
    genre_id_to_str = {i: genre for i, genre in enumerate(genres)}

    users = read_users('data/ratings.csv', movies, genre_str_to_id)

    pprint(genre_str_to_id)
    for user in users.values():
        user.print_genre_ratings(genre_id_to_str)
    # print("Genres: {}".format(genres))
    # print(movies)


if __name__ == '__main__':
    main()
