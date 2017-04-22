import csv
import typing


class CastRecord:
    def __init__(self, film_id, film_title, actor_name, role_type, role_prefix, role_content):
        """
        Fields explanation: http://archive.ics.uci.edu/ml/machine-learning-databases/movies-mld/doc.html
        Args:
            film_id:
            film_title:
            actor_name:
            role_type:
            role_prefix: R  - role known, listed in role_content
                         RZ - role uncertain
                         RN - role name known
                         RU - role unknown
            role_content:
        """
        super().__init__()
        self.film_id = film_id
        self.film_title = film_title
        self.actor_name = actor_name
        self.role_type = role_type
        self.role_prefix = role_prefix
        self.role_content = role_content

    def __str__(self, *args, **kwargs):
        return "{} - {}".format(self.film_title, self.actor_name)

    @staticmethod
    def parse(csv_row: typing.List[str]):
        roles = csv_row[4].split(':', 1)
        role_prefix = roles[0]
        try:
            role_content = roles[1]
        except IndexError:
            role_content = ""

        return CastRecord(csv_row[0], csv_row[1], csv_row[2], csv_row[3], role_prefix, role_content)


def load_data(fn):
    data = []

    with open(fn) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            data.append(row)

    return data


import networkx


def create_graph(records: typing.List):
    film_actors = {}  # Mapping {film: [act1, act2]}
    g = networkx.Graph()
    for record in records:
        g.add_node(record.actor_name)

        if record.film_title not in film_actors:
            film_actors[record.film_title] = []
        film_actors[record.film_title].append(record.actor_name)

    for film, actor_list in film_actors.items():
        for actor in actor_list:
            for other_actor in actor_list:
                if actor != other_actor:
                    g.add_edge(actor, other_actor)
                    # print("Adding edge between [{}] - [{}]".format(actor, other_actor))

    return g


def main():
    data = load_data('casts.csv')
    records = []
    for row in data:
        records.append(CastRecord.parse(row))
        print(records[-1])
        if records[-1].actor_name == ":":
            exit()

    # graph = create_graph(records[:500])
    graph = create_graph(records)
    networkx.write_gexf(graph, 'exported_graph.gexf')


if __name__ == '__main__':
    main()
