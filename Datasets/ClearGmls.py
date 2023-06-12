# -*- coding: UTF-8 -*-
import networkx as nx
import os

def clearGml(gmlPath):
	G = nx.read_gml(gmlPath, destringizer=int)
	nodos = dict(G.nodes())

	for n in nodos:
		if('hIndex' in nodos[n]):
			pass
			# nodos[n]['numCoAuthors'] = sum(1 for _ in G.neighbors(n))
			# print(nodos[n]['numCoAuthors'])

	for n in nodos:
		if('hIndex' not in nodos[n]):
			G.remove_node(n)

	nx.write_gml(G, "gmls/ExploredAuthors.gml")


clearGml("gmls/710_authors.gml")

