# -*- coding: UTF-8 -*-
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import traceback
import time


G = nx.read_gml('gml\\Mod_0 It_2.gml')
G_c = nx.Graph()

att = 'areas'

nodos = G.nodes()

#print(nodos)

indexes = set()

for n in nodos:
	try:
		for area in nodos[n][att]:
			indexes.add(area)
	except:
		pass

indexes = list(indexes)

for country in indexes:
	G_c.add_node(country)

matPesos = np.zeros((len(indexes),len(indexes)))
matConn = np.zeros((len(indexes),len(indexes)))

for n in nodos:
	try:
		areas = nodos[n][att]
		for i in range(0,len(areas)):
			for j in range(i+1,len(areas)):
				if G_c.has_edge(areas[i],areas[j]):
					G_c[areas[i]][areas[j]]['weight'] +=1
				else:
					#Cria conexao de peso 1, se nao existir uma
					G_c.add_edge(areas[i], areas[j], weight=1)
	except:
		pass

name = 'gml\\Areas.gml'
nx.write_gml(G_c, str(name))