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


def report_general_statistics(graph: networkx.Graph):
    nodes = graph.number_of_nodes()
    edges = graph.number_of_edges()
    density = edges / (nodes * (nodes - 1) / 2)

    print("=" * 80)
    print("""BASIC STATISTICS:
Number of nodes: {nodescnt})
Number of edges: {edgescnt}
Density: {density}
Number of components: {components}"""
          .format(nodescnt=graph.number_of_nodes(),
                  edgescnt=graph.number_of_edges(),
                  density=density,
                  components=networkx.number_connected_components(graph)
                  ))
    print("=" * 80)


def report_centralities(graph: networkx.Graph):
    centralities_tostr_dict = {networkx.degree_centrality: 'degree_centrality',
                               networkx.closeness_centrality: 'closeness_centrality',
                               networkx.betweenness_centrality: 'betweenness_centrality',
                               networkx.eigenvector_centrality: 'eigenvector_centrality'}
    centralities = [networkx.degree_centrality, networkx.closeness_centrality,
                    networkx.betweenness_centrality, networkx.eigenvector_centrality]

    print("=" * 80)
    print("CENTRALITIES:")
    for centrality in centralities:
        centrality_res = centrality(graph)

        # Add as node attribute
        for actor, centrality_val in centrality_res.items():
            graph[actor][centralities_tostr_dict[centrality]] = centrality_val

        centrality_res_sorted = sorted(centrality_res.items(), key=lambda element: element[1], reverse=True)
        print("{} - top 10: ".format(centrality))
        print("  {}".format(", ".join([elm[0] for elm in centrality_res_sorted[:10]])))
    print("=" * 80)


def report_communities(graph: networkx.Graph):
    communities = {}
    for community_id, community in enumerate(networkx.k_clique_communities(graph, 3)):
        for node in community:
            communities[node] = community_id + 1

    # Group actors from same communities together
    community_to_actors = {}
    for key, val in communities.items():
        if val not in community_to_actors:
            community_to_actors[val] = []
        community_to_actors[val].append(key)

    # Sort based on the length of the list of actors
    community_to_actors_sorted = sorted(community_to_actors.items(), key=lambda element: len(element[1]), reversed=True)

    print("=" * 80)
    print("COMMUNITIES:")
    for community in community_to_actors_sorted[:10]:
        print("ID {}, {} actors: {}".format(community[0], len(community[1]), ", ".join(community[1])))
    print("=" * 80)

    # Add as attribute to graph
    for actor, community_id in communities.items():
        graph.node[actor]['community'] = community_id


def main():
    data = load_data('casts.csv')
    records = []
    for row in data:
        records.append(CastRecord.parse(row))
        # print(records[-1])
        # if records[-1].actor_name == ":":
        #     exit()

    # graph = create_graph(records[:500])
    graph = create_graph(records)
    # networkx.write_gexf(graph, 'exported_graph.gexf')

    report_general_statistics(graph)
    report_centralities(graph)


if __name__ == '__main__':
    main()
