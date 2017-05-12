import csv

SKIP_GENRES = ['(no genres listed)']


class User:
    def __init__(self, user_id, ratings):
        super().__init__()
        self.id = user_id
        self.ratings = ratings


class Movie:
    def __init__(self, movie_id, title, genres):
        super().__init__()
        self.id = movie_id
        self.title = title
        self.genres = genres


def read_movies(fn):
    """
    Read datafile with movies.
    :param fn:
    :return: Tuple: (
                     dict of Movie objects (key = movie_id),
                     set of genres (as strings)
                    )
    """

    genres_set = set()
    movies = {}

    with open(fn, encoding="utf-8") as f:
        f.readline()
        f.readline()
        reader = csv.reader(f, delimiter=',')
        for movie_row in reader:
            print("Row: {}".format(movie_row))
            movie_id = movie_row[0]
            title = movie_row[1]
            genres = [genre.strip() for genre in movie_row[2].split('|') if genre.strip() not in SKIP_GENRES]
            movie = Movie(movie_id, title, genres)
            movies[movie_id] = movie
            genres_set = genres_set.union(set(genres))

    return movies, genres_set


def main():
    movies, genres = read_movies('data/movies.csv')

    print("Genres: {}".format(genres))


if __name__ == '__main__':
    main()
