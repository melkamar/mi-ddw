import numpy
from typing import Dict, List, Tuple


def main():
    numpy.set_printoptions(linewidth=1000, suppress=True)

    # matrix_H = create_h('data/edux.txt')
    matrix_H = create_h('data/test1.txt')  # cyklus - hodnoty oscilují a nekonverguje to
    # matrix_H = create_h('data/test2.txt')  #
    # matrix_H = create_h('data/test3.txt')  # Při větším počtu iterací se u H PR úplně vynuluje - sink
    # matrix_H = create_h('data/test4.txt')  #

    print('Matrix H ' + '=' * 80)
    print(matrix_H)
    print('=' * 80)

    matrix_S = create_s(matrix_H)
    print('Matrix S ' + '=' * 80)
    print(matrix_S)
    print('=' * 80)

    # Damping (alpha) - if 1, equals to S. if 0, PR is not recalculated at all.
    #
    matrix_G = create_g(matrix_S, 0.85)
    print('Matrix G ' + '=' * 80)
    print(matrix_G)
    print('=' * 80)

    iterations = 10
    pr_h = computePR(matrix_H, iterations)
    print("\n\n")
    pr_s = computePR(matrix_S, iterations)
    print("\n\n")
    pr_g = computePR(matrix_G, iterations)

    print('PageRank H ' + '=' * 80)
    print(pr_h)
    print('=' * 80)

    print('PageRank S ' + '=' * 80)
    print(pr_s)
    print('=' * 80)

    print('PageRank G ' + '=' * 80)
    print(pr_g)
    print('=' * 80)


def create_h(fn):
    with open(fn) as f:
        nodes_count = int(f.readline())
        matrix_H = numpy.zeros((nodes_count, nodes_count))

        for row, line in enumerate(f):
            edges = line.split()
            for edge in edges:  # edge: str x:y
                edge_from, edges_count = edge.split(':')
                edge_from = int(edge_from)
                edges_count = int(edges_count)

                # divide each node item in matrix by how many edges lead out of the given node
                matrix_H[row, edge_from] = edges_count / len(edges)

        return matrix_H


def create_s(matrix_H):
    matrix_S = matrix_H.copy()

    matrix_size = matrix_S.shape[0]

    for row in range(0, matrix_size):
        row_sum = matrix_S[row, :].sum()
        if row_sum == 0:  # no edges from this node -> fake edges to all the nodes
            matrix_S[row, :] = [1 / matrix_size] * matrix_size

    return matrix_S


def create_g(matrix_S, alpha):
    matrix_G = matrix_S.copy()

    matrix_size = matrix_G.shape[0]
    e = numpy.ones(matrix_size)

    matrix_G = alpha * matrix_S + \
               (1 - alpha) * (1 / matrix_size) * e * e.transpose()

    return matrix_G


def computePR(matrix, iterations):
    matrix_size = matrix.shape[0]

    pagerank = numpy.zeros(matrix_size)

    # Inicializace - stejná hodnota ve všech prvcích
    # for i in range(0, matrix_size):
    #     pagerank[i] = 1/matrix_size

    # Inicializace - jen jeden prvek je 1, zbytek 0
    pagerank[0] = 1

    for i in range(iterations):
        pagerank = pagerank.transpose() @ matrix
        print(f"PageRank #{i}: {pagerank}   ---  vector sum: {pagerank.sum()}")

    return pagerank


if __name__ == '__main__':
    main()
