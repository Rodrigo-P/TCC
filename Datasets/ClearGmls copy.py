# -*- coding: UTF-8 -*-
import networkx as nx

def clearGml(gmlPath):
	G = nx.read_gml(gmlPath, destringizer=int)
	nodos = dict(G.nodes())

	for n in nodos:
		if('hIndex' in nodos[n]):
			try:
				nodos[n]['Citations'] = int(nodos[n]['Citations'])
			except:
				nodos[n]['Citations'] = int(nodos[n]['Citations'].replace(',', ''))

			try:
				nodos[n]['Documents'] = int(nodos[n]['Documents'])
			except:
				nodos[n]['Documents'] = int(nodos[n]['Documents'].replace(',', ''))

			try:
				nodos[n]['hIndex'] = int(nodos[n]['hIndex'])
			except:
				nodos[n]['hIndex'] = int(nodos[n]['hIndex'].replace(',', ''))

			nodos[n]['Areas'] = nodos[n]['Areas'][0]
			nodos[n]['Explored'] = True
		else:
			nodos[n]['Explored'] = False

	nx.gexf.write_gexf(G, "gmls/clean.gexf")
	# nx.gml.write_gml(G, "gmls/clean.gml")

clearGml("gmls/710_authors.gml")

