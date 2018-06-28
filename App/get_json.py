import networkx as nx
from networkx.readwrite import json_graph
from itertools import islice
import json


def window(seq, n=2):
    it = iter(seq)
    result = tuple(islice(it, n))
    if len(result) == n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result


def get(df):

    gdf = df.sort_values(["Student Number", "Term"]) \
            .loc[:, ["Student Number", "Term", "Node Column"]] \
            .groupby("Student Number")

    a = list(gdf["Node Column"])

    flow = [[el for el in x[1]] for x in a]

    sankey = [list(window([str(i) + x for i, x in enumerate(sub)])) for sub in flow]
    sankey = [item for sublist in sankey for item in sublist]

    s = nx.DiGraph()
    for edge in sankey:
        if s.has_edge(*edge):
            s[edge[0]][edge[1]]['weight'] += 1
        else:
            s.add_edge(*edge, weight=1)

    jdat = json_graph.node_link_data(s)

    return jdat
