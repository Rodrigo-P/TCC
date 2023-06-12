# -*- coding: UTF-8 -*-
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import traceback
import time


G = nx.read_gml('gmls/Mod_0 It_2.gml')
G_c = nx.Graph()

att = 'country'

nodos = G.nodes()

#print(nodos)

indexes = set()

for n in nodos:
	try:
		indexes.add(nodos[n][att])
	except:
		pass

indexes = list(indexes)

for country in indexes:
    G_c.add_node(country)

matPesos = np.zeros((len(indexes),len(indexes)))
matConn = np.zeros((len(indexes),len(indexes)))


for P0, P1, D in G.edges(data=True):
	try:
		P0 = nodos[P0][att]
		P1 = nodos[P1][att]
		if G_c.has_edge(P0,P1):
			G_c[P0][P1]['weight'] = G_c[P0][P1]['weight'] + D['weight']
		else:
			#Cria conexao, se nao existir uma
			G_c.add_edge(P0, P1, weight=G_c[P0][P1]['weight'])
	except:
		pass

name = 'gmls\\Paises.gml'
nx.write_gml(G_c, str(name))