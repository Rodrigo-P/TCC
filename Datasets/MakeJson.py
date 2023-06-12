# -*- coding: UTF-8 -*-
import networkx as nx
import random
import os

def makeDataLine(arqX, G, P0, P1):
	atributosBin = ['Country', 'City', 'Institution']
	atributosProp =	['hIndex', 'Citations', 'Documents']
	dado = "{"
	nodos = G.nodes

	for att in atributosBin:
		# print(att, nodos[P0][att], nodos[P1][att])

		dado += "\""+ att +"\": "
		if(nodos[P0][att] == nodos[P1][att]):
			dado += "1.0,"
		else:
			dado += "0.0,"

	for att in atributosProp:
		# print(att, nodos[P0][att], nodos[P1][att])

		dado += "\""+ att +"\": "

		
		try:
			att0 = int(nodos[P0][att])
		except:
			att0 = int(nodos[P0][att].replace(',', ''))
		try:
			att1 = int(nodos[P1][att])
		except:
			att1 = int(nodos[P1][att].replace(',', ''))
		# att1 = int(nodos[P1][att])


		if(att0 > att1):
			dado += f"{att1/att0:.5f},"
		elif(att1 != 0):
			dado += f"{att0/att1:.5f},"
		else:
			dado += "1.0,"

	cnbors = list(nx.common_neighbors(G, P0, P1))
	union_size = len(set(G[P0]) | set(G[P1]))

	dado += "\"jaccardCoef\": "
	dado += f"{len(cnbors)/union_size:.5f},"

	A0 = nodos[P0]['Areas']
	A1 = nodos[P1]['Areas']

	if(type(A0) == str):
		A0 = [A0]
	if(type(A1) == str):
		A1 = [A1]

	allAreas = list(set(A0 + A1))

	numCommonAreas = len(A0) + len(A1) - len(allAreas)

	dado += f"\"Areas\": {numCommonAreas/len(allAreas):.5f}"

	dado += "}\n"

	# print(dado, "\n")
	arqX.write(dado)

def makeJson(filePath):
	G = nx.gml.read_gml(filePath, destringizer=int)
	nodos = G.nodes()

	output = 'jsons\\' + filePath[5:-4]

	arqX = open(output + '_X.json', "w", encoding='utf8')
	arqY = open(output + '_Y.json', "w", encoding='utf8')

	count = 0

	print(len(G.edges))

	for P0, P1, D in G.edges(data=True):
		if('hIndex' in nodos[P0] and 'hIndex' in nodos[P1]):
			makeDataLine(arqX, G, P0, P1)
			arqY.write('{"connected": 1.0}\n')
			count += 1

	nodosL = list(nodos)
	random.shuffle(nodosL)

	for i in range(len(nodosL)):
		for j in range(i + 1, len(nodosL)):
			P0 = nodosL[i]
			P1 = nodosL[j]
			if('hIndex' in nodos[P0] and 'hIndex' in nodos[P1] and not G.has_edge(P0, P1)):
					makeDataLine(arqX, G, P0, P1)
					arqY.write('{"connected": 0.0}\n')
					count -= 1
					if(count == 0):
						break
		if(count == 0):
			break

	arqX.close()
	arqY.close()

gml_path = "gmls/main.gml"

makeJson(gml_path)