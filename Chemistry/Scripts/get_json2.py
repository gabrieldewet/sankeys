import networkx as nx
from networkx.readwrite import json_graph
from itertools import islice


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
            .loc[:, ["Student Number", "Term", "Node Column", "Group"]] \
            .groupby(["Student Number","Group"])

    a = list(gdf["Node Column"])

    flow = [[[el for el in x[1]],x[0][1]] for x in a]
    
    sankey1 = [ [list( window([str(i) + x for i, x in enumerate(sub[0])]) ),sub[1] ]for sub in flow]
    sankey = [[item,sublist[1]] for sublist in sankey1 for item in sublist[0]]


    s = nx.MultiDiGraph()
    for edge in sankey:

        if s.has_edge(*edge[0],key=edge[1]):
            s[edge[0][0]][edge[0][1]][edge[1]]['weight'] += 1
        else:
            s.add_edge(*edge[0], weight=1, color=edge[1], key=edge[1])
        

    jdat = json_graph.node_link_data(s)

    return jdat
