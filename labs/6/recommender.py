import csv
from sklearn.metrics.pairwise import cosine_similarity


class UserRating:
    def __init__(self, name, ratings):
        super().__init__()
        self.name = name
        self.ratings = ratings

    @staticmethod
    def parse(csv_entry):
        name = csv_entry[0]
        ratings = csv_entry[1:]
        return UserRating(name, ratings)

    def __str__(self, *args, **kwargs):
        return f"User {self.name} ({self.ratings})"


def read_input(fn):
    with open(fn) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            yield row


def main():
    data = read_input('small-dataset.csv')
    user_ratings = []
    for row in data:
        user_ratings.append(UserRating.parse(row))
        print(f"Added {user_ratings[-1]}")


if __name__ == '__main__':
    main()
