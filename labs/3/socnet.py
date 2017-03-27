import nltk
import networkx
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pyplot as plt
from pprint import pprint


def _extract_entities(ne_chunked):
    data = {}
    for entity in ne_chunked:
        if isinstance(entity, nltk.tree.Tree):
            text = " ".join([word for word, tag in entity.leaves()])
            ent = entity.label()
            data[text] = ent
        else:
            continue
    return data


def get_entities(tokens):
    tagged = nltk.pos_tag(tokens)

    ne_chunked = nltk.ne_chunk(tagged, binary=True)
    return _extract_entities(ne_chunked)


# input text
with open('greek-mythology.txt', 'r') as f:
    text = f.read()

# process text and convert to a graph
sentences = [[t for t in nltk.word_tokenize(sentence)] for sentence in nltk.sent_tokenize(text)]

graph = networkx.Graph()
# print(graph.nodes())
# exit(2)

for sentence in sentences[:20]:
    entities = get_entities(sentence)
    for key, value in entities.items():
        graph.add_node(key)

    for key, value in entities.items():
        for key2, value2 in entities.items():
            graph.add_edge(key, key2)


def report_stats(graph):
    print(
        """
        Nodes: {nodes_count}
        Edges: {edges_count}
        Density: {density} edges/node
        """.format(nodes_count=len(graph.nodes()),
                   edges_count=len(graph.edges()),
                   density=len(graph.edges()) / len(graph.nodes()))
    )

    print("-" * 80)
    print("Components")
    for component in networkx.connected_components(graph):
        print(component)
    print("-" * 80)


def report_centralities(graph):
    centralities = [networkx.degree_centrality, networkx.closeness_centrality,
                    networkx.betweenness_centrality, networkx.eigenvector_centrality]
    region = 220
    for centrality in centralities:
        region += 1
        plt.subplot(region)
        plt.title(centrality.__name__)
        networkx.draw(graph, font_size=8, pos=networkx.circular_layout(graph), labels={v: str(v) for v in graph},
                      cmap=plt.get_cmap("bwr"), node_color=[centrality(graph)[k] for k in centrality(graph)])
    plt.savefig("centralities.png")


def report_communities(graph):
    communities = {node: cid + 1 for cid, community in enumerate(networkx.k_clique_communities(graph, 3)) for node in
                   community}

    pos = networkx.circular_layout(graph)
    networkx.draw(graph, pos, font_size=8,
                  labels={v: str(v) for v in graph},
                  cmap=plt.get_cmap("rainbow"),
                  node_color=[communities[v] if v in communities else 0 for v in graph])
    plt.savefig("communities.png")


report_stats(graph)
report_centralities(graph)
report_communities(graph)

# exit(2)

# write to GEXF
networkx.write_gexf(graph, "export.gexf")
