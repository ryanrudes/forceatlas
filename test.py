import matplotlib.pyplot as plt
import forceatlas as fa2
import networkx as nx

G = nx.fast_gnp_random_graph(100, 0.1)
pos = fa2.fa2_layout(G, iterations = 10000, threshold = 1e-3)

nx.draw(G)
plt.savefig("graph.png")