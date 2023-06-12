# -*- coding: UTF-8 -*-
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import traceback
import time


G = nx.read_gml('gmls/Mod_0 It_2.gml')

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

matPesos = np.zeros((len(indexes),len(indexes)))
matConn = np.zeros((len(indexes),len(indexes)))


for P0, P1, D in G.edges(data=True):
	w = D['weight']
	try:
		P0 = nodos[P0][att]
		P1 = nodos[P1][att]

		matPesos[indexes.index(P0)][indexes.index(P1)] += D['weight']
		matConn[indexes.index(P0)][indexes.index(P1)] += 1
	except Exception as e:
		pass

matPesos = matPesos/matPesos.sum()
matConn = matConn/matConn.sum()

indPesos = np.unravel_index(np.argmax(matPesos, axis=None), matPesos.shape)
indConn = np.unravel_index(np.argmax(matConn, axis=None), matConn.shape)

sumX = matPesos.sum(axis=0)
sumY = matPesos.sum(axis=1)
aibi = np.sum(sumX[:]*sumY[:])
eii = np.trace(matPesos)

rPesos = (eii-aibi)/(1-aibi)

sumX = matConn.sum(axis=0)
sumY = matConn.sum(axis=1)
aibi = np.sum(sumX[:]*sumY[:])
eii = np.trace(matConn)

rConn = (eii-aibi)/(1-aibi)

print("Matriz com Pesos")
print(indexes[indPesos[0]], indexes[indPesos[1]], sep = "; ")
print("Max =", matPesos[indPesos[1]][indPesos[0]])
print("R =", rPesos)

print("\nMatriz sem Pesos")
print(indexes[indConn[0]], indexes[indConn[1]], sep = "; ")
print("Max =", matConn[indConn[1]][indConn[0]])
print("R =", rConn)

#print("\n\nNetworkx R =", nx.attribute_assortativity_coefficient(G, attribute = 'hIndex'))

fig, ax = plt.subplots(ncols = 4, gridspec_kw={"width_ratios":[1, 0.04, 1, 0.04]})

imPesos = ax[0].pcolormesh(matPesos)
imConn = ax[2].pcolormesh(matConn)

fig.colorbar(imPesos, cax = ax[1])
fig.colorbar(imConn, cax = ax[3])

plt.subplots_adjust(left = 0.05, right = 0.95, top = 0.95, bottom = 0.05)

plt.show()


'''
for i in range(matPesos.shape[0]):
	eii += matPesos[i][i]
	aibi += sumX[i]*sumY[i]
	pass
'''