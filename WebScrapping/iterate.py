# -*- coding: UTF-8 -*-

from networkx.readwrite.adjlist import write_adjlist
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.opera import OperaDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from unidecode import unidecode
from selenium import webdriver
from bs4 import BeautifulSoup

import matplotlib.pyplot as plt
import networkx as nx
import traceback
import time
import io

def addArt(G,title,names,year,source,citations,ids,mode):
	#Cria conexoes entre todos os pesquisadores
	for x in range(0,len(names)):
		for y in range(x+1,len(names)):
			#Checa se os outros pesquisadores ja existem
			#Feita por meio do id, que e unico e nao varia como o nome citado
			#Nao e necessario checar o primeiro pois e sempre o pesquisador da pagina visitada
			#Este ja foi adicionado quando sua pagina foi visitada
			if(ids[y] not in G.nodes()):
				#Adiciona, caso o pesquisador seja novo no grafo
				G.add_node(ids[y],name=names[y])
			#Modo de conexao por artigo
			if mode:
				#Adiciona edge com nome do artigo, e suas informacoes
				G.add_edge(ids[x],ids[y],key=title,year=year,source=source,citations=citations)
			#Modo de conexao por peso
			else:
				#Aumenta o peso se ja houver uma conexao
				if G.has_edge(ids[x],ids[y]):
					G[ids[x]][ids[y]]['weight']=G[ids[x]][ids[y]]['weight']+1
				#Cria conexao de peso 1, se nao existir uma
				else:
					G.add_edge(ids[x],ids[y],weight=1)

def addPerson(driver,G,url,mode):
	global url_pos
	
	i=0
	year=0
	title=""
	source=""
	num_arts=0
	citations=0

	#Ponteiro para botao que vai para a proxima pagina
	#Inicializado para entrar no while
	nxt=1
	
	#Contador para ir para proximas paginas
	page=1

	#Lista de urls para proxima camada
	urls=[]

	#Lista de ids 
	#Primeiro id e o pesquisador visitado
	ids=[int(url[url.index("Id=")+3:])]
	
	#Abre pagina
	driver.get(url)
	#Delay para evitar problemas com o servidor
	time.sleep(1)
	element_present = EC.presence_of_element_located((By.CSS_SELECTOR, "a[title='Show document details']"))
	WebDriverWait(driver, 60).until(element_present)

	#Obtem source code da pagina
	soup=BeautifulSoup(driver.page_source,'lxml')
	
	#file=open("Edu_source_inside.html","w")
	#file.write(str(soup))
	#file.close()

	#Usado para encontrar o h-index
	#Valor aparecer apos a segunda mensao de h na pagina
	span=soup.find_all("span")
	h_index=0

	#Coleta areas de estudo
	badges=driver.find_element_by_css_selector("micro-ui[component-id='scopus-author-general-information']")
	data=badges.get_attribute('datastring')
	
	data = unidecode(data)

	name = data[data.find("full\":\"")+7:]
	name = name[0:name.find("\"")]
	
	#Lista de nomes dos pesquisadores
	#Adiciona nome do pesquisador como primeiro da lista
	names = [name]

	uni = data[data.find("latestAffiliatedInstitution\":")+28:]
	uni = uni[uni.find("name\":\"")+7:]
	uni = uni[:uni.find("\"")]
	
	country = data[data.find("country\":\"")+10:]
	country = country[:country.find("\"")]

	city = data[data.find("city\":\"")+7:]
	city = city[:city.find("\"")]
	
	h_index = data[data.find("hindex\":")+8:]
	h_index = h_index[:h_index.find(",")]
	
	numCits = data[data.find("citationsCount\":")+16:]
	numCits = numCits[:numCits.find(",")]

	numDocs = data[data.find("documentCount\":")+15:]
	numDocs = numDocs[:numDocs.find(",")]	

	numCoAuthors = data[data.find("coAuthorsCount\":")+16:]
	numCoAuthors = numCoAuthors[:numCoAuthors.find(",")]	

	areaData=data[data.find("publishedSubjectAreas\":[")+24:]
	areaData = areaData[:areaData.find("]")]
	areas = []

	pos = areaData.find("name\":\"")+7
	while pos != 6:
		areaData = areaData[pos:]
		areas.append(areaData[:areaData.find("\"")])
		pos = areaData.find("name\":\"")+7

	#Altera o nodo para o nome completo encontrado na pagina da pessoa
	#Tambem adiciona areas, intituicao, cidade e pais
	try:
		if areas == []:
			areas = ""
		if '[' in country:
			country = "Unkown"
		
		G.add_node(ids[0],
					hIndex=h_index,
					name=name,
					country=country,
					city=city,
					institution=uni,
					areas=areas,
					numCits = numCits,
					numDocs = numDocs,
					numCoAuthors = numCoAuthors)
	except:
		G.add_node(ids[0], hIndex=h_index, name=name, institution=uni, areas=areas)
		print("\a***li FAIULRE***\a")
		file=open("Web_Scrap\\Fails\\li_"+str(ids[0])+".txt", "w", encoding="utf-8")
		file.write(str(soup))
		file.close()

	#Loop para visitar todas as paginas
	while nxt!=None:
		#Coleta source code e obtem todos os elementos de artigos
		div_art = soup.find_all("div",{"data-component": "document-source"})
		arts = soup.find_all("a",{"title": "Show document details"})
		div_author = soup.find_all("div",{"class": "author-list"})
		all_citations = soup.find_all("a",{"class": "link info-field__value"})

		num_arts+=len(div_author)


		for i in range(0,len(div_author)):
			art = div_author[i]
			#Encontra todos os filhos do tipo <a> 
			a=art.find_all("a")

			#Percorre o resto dos hiperlinks coletando os pesquisadores que participaram
			for j in range(0,len(a)-1):
				try:
					#Obtem id do pesquisador
					href=str(a[j]['href'])
					index=href.index("Id=")+3
					tmp_id=int(href[index:])
				except:
					#Erro ocorre quando ha (...) nas citacoes
					continue
				if (tmp_id not in ids):
					#Adiciona pesquisador que ainda nao estao na lista para este artigo
					tmp = a[j].contents[0].contents[0]
					names.append(unidecode(tmp.lower()))
					ids.append(tmp_id)
					if(href not in urls):
						urls.append(href)

			#Pega dados para modo de conexao por artigo
			if mode:
				#Nome da publicacao
				try:
					#Remove acentos do titulo
					#Evita problemas de codificacao
					title=unidecode(arts[i].contents[0])
				except:
					#Unidecode gera erro caso o titulo contenha caracteres superscript
					#Remocao e feita por meio de "try catch" pois esse problema e raro
					#Dessa forma e mais eficiente so tentar remover os caracteres caso eles existam
					title=str(arts[i].contents[0])
					for ch in ['⁰','¹','²','³','⁴','⁵','⁶','⁷','⁸','⁹']:
						title=title.replace(ch," ")
					title=unidecode(title)

				revista = div_art.find_all("span")
				#Revista onde foi publicada
				source = revista[0].contents[0]
				source=unidecode(source.replace('\n',''))

				#Ano de publicacao
				source = revista[1].contents[0]
				year=year.replace('\n','')		

				#Numero de citacaoes
				cit=citations[i]['title']
				cit=cit[:cit.find(" ")]

				#Adiciona o trabalho
				addArt(G,title,names,year,source,cit,ids,mode)
			else:
				#Adiciona o trabalho
				addArt(G,"",names,0,"",0,ids,mode)
			

			#Limpa lista de nomes e ids
			#Nao elimina o pesquisador sendo visitado
			del names[1:]
			del ids[1:]

		#Tenta acessar a proxima pagina
		try:
			nxt=driver.find_element_by_css_selector("button[data-page-index=\""+str(page)+"\"]")
			page+=1
			nxt.click()
			time.sleep(3)
			
			soup=BeautifulSoup(driver.page_source,'lxml')
		except:
			#Imprime dados do pesquisador no terminal
			print('{:4s}/{:4s}|{:12s}|{:42s}|{:3s}|{:4s} artigos|'.format(str(url_pos),str(len(layer_urls)),str(ids[0]),names[0],str(h_index),str(num_arts)))
			nxt=None
	if(num_arts==0):
		print("\a***0 Artigos***\a")
		file=open("Web_Scrap\\Fails\\Arts=0_"+str(ids[0])+".txt", "w", encoding="utf-8")
		file.write(str(soup))
		file.close()


	#Retorna todos os urls encontrados
	return urls

#https://www.webometrics.info/en/hlargerthan100
#Urls Iniciais
starting_urls = [
				# "https://www.scopus.com/authid/detail.uri?authorId=7202074046", 	#Kessler, Ronald C. 		N.0001
				# "https://www.scopus.com/authid/detail.uri?authorId=57203046809",	#Manson, Jo Ann E. 			N.0002
				# "https://www.scopus.com/authid/detail.uri?authorId=57206520256",	#Colditz, Graham A.			N.0003
				# "https://www.scopus.com/authid/detail.uri?authorId=7402409226",	#Langer, Robert Samuel M.	N.0004
				# "https://www.scopus.com/authid/detail.uri?authorId=35606519600",	#Jackson, Jeremy B.C.		N.0005
				# "https://www.scopus.com/authid/detail.uri?authorId=35396685700",	#Akira, Shizuo				N.0006
				# "https://www.scopus.com/authid/detail.uri?authorId=36077704000",	#Vogelstein, Bert			N.0007
				# "https://www.scopus.com/authid/detail.uri?authorId=35463345800",	#Grätzel, M.				N.0008
				# "https://www.scopus.com/authid/detail.uri?authorId=36038688700",	#Hu, Frank B.				N.0009
				# "https://www.scopus.com/authid/detail.uri?authorId=8841196600",	#Guyatt, Gordon Henry M.	N.0010
				# "https://www.scopus.com/authid/detail.uri?authorId=35373488900",	#Cummings, Steven Ron		N.0100
				# "https://www.scopus.com/authid/detail.uri?authorId=36013862000",	#Nakamura, Yusuke			N.0101
				# "https://www.scopus.com/authid/detail.uri?authorId=7501533080",	#Wilson, Richard D.			N.0102
				# "https://www.scopus.com/authid/detail.uri?authorId=35375959000",	#Stanley, H. Eugene			N.0103
				# "https://www.scopus.com/authid/detail.uri?authorId=35492852400",	#Ajayan, Pulickel M.		N.0104
				# "https://www.scopus.com/authid/detail.uri?authorId=7402574751",	#Reíter, Rüssel J.			N.0105
				# "https://www.scopus.com/authid/detail.uri?authorId=55913409300",	#Tyler, Tom R.				N.1000
				# "https://www.scopus.com/authid/detail.uri?authorId=7006099014",	#Mantzoros, Christos S.		N.1001
				# "https://www.scopus.com/authid/detail.uri?authorId=34573429300",	#Sham, Pak Chung			N.1002
				# "https://www.scopus.com/authid/detail.uri?authorId=7005510490",	#Ribas, Antoni				N.1003
				# "https://www.scopus.com/authid/detail.uri?authorId=35227997700",	#Slutsky, Arthur S.			N.1004
				# "https://www.scopus.com/authid/detail.uri?authorId=18038298200",	#Pałka, Marek				N.1005
				# "https://www.scopus.com/authid/detail.uri?authorId=7103120387",	#Driessen, Arnold J.M.		N.4725
				# "https://www.scopus.com/authid/detail.uri?authorId=7005903711",	#Hilsenbeck, Susan G.		N.4726
				# "https://www.scopus.com/authid/detail.uri?authorId=26643614600",	#Kopecek, Jindrich I.		N.4727
				# "https://www.scopus.com/authid/detail.uri?authorId=10840422600",	#Elde, Robert P.			N.4728
				# "https://www.scopus.com/authid/detail.uri?authorId=7202938057",	#Foster, Tim J.				N.4729
				# "https://www.scopus.com/authid/detail.uri?authorId=8502005900",	#Labbé, Ivo					N.4730
				# "https://www.scopus.com/authid/detail.uri?authorId=7004586426",	#Kolodner, Paul
				# "https://www.scopus.com/authid/detail.uri?authorId=35317963900",	#Kürths, Jürgen
				# "https://www.scopus.com/authid/detail.uri?authorId=55958178100",	#Hertz, Paul
				# "https://www.scopus.com/authid/detail.uri?authorId=16553015400",	#Neilsen, Joseph
				# "https://www.scopus.com/authid/detail.uri?authorId=10140494200",	#Rodrigues, Francisco Aparecido
				]


max_pesq = 500
url_pos = 0

#Lista de urls visitados
urls = []

#Urls da camada atual
layer_urls = []

#Urls da camada seguinte
nxt_urls=set()

#Inicializacao do browser
#driver = webdriver.Chrome(ChromeDriverManager().install())
driver = webdriver.Opera(executable_path = "C:\\Users\\Rodrigo\\Desktop\\Rodrigo\\USP\\IC\\cods\\Web_Scrap\\drivers\\operadriver.exe")

driver.get(starting_urls[0])

print("(0)Peso | (1)Artigo")
mode=int(input("Tipo de Edge: "))
iterations=int(input("\nNumero de camadas: "))
if mode:
	G=nx.MultiGraph()
else:
	G=nx.Graph()

soup = BeautifulSoup(driver.page_source,'lxml')

file = open("htmls\\Edu_source_outside.html", "w", encoding="utf-8")
file.write(str(soup))
file.close()

time.sleep(2)

for first in starting_urls:
	#Limpa listas
	layer_urls = [first]
	nxt_urls.clear()
	urls.clear()
	G.clear()

	i = 0
	#Adiciona camadas
	while(i < iterations and len(urls) < max_pesq):
		#Numero de pessoas a serem analisadas na camada atual
		print(len(layer_urls))
		url_pos = 0

		#Adiciona todas as pessoas da camada atual
		for x in layer_urls:
			if(len(urls) > max_pesq):
				break
			url_pos+=1
			#Checa se o pesquisador ja foi visitado
			if(x not in urls):
				try:
					#Adiciona todos os pesquisadores encontrados na pagina
					nxt_urls.update(addPerson(driver,G,x,mode))

					#Adiciona a lista de ja visitados
					urls.append(x)

				#Evita que o programa finalize sem salvar
				#Caso ocorra problemas de conexao
				except Exception as e:
					traceback.print_exc()
					try:
						soup=BeautifulSoup(driver.page_source,'lxml')
						file=open("Web_Scrap\\Fails\\CallFailed"+str(x)[-15:-1]+".html", "w", encoding="utf-8")
						file.write(str(e)+"\n\n"+str(x)+"\n\n")
						file.write(str(soup))
						file.close()
					except:
						pass
					print("\n\n\aCall Failed|\a"+str(e)+"\a|\a"+x)
					if(str(e).startswith("Message: chrome not reachable")):
						break
		#Limpa lista da camada atual e passa para a proxima
		layer_urls=list(nxt_urls)

		#Limpa lista da camada seguinte
		nxt_urls.clear()
		i+=1

	name = 'gmls\\'+urls[0][urls[0].index("Id=")+3:]+'_Mod_'+str(mode)+' It_'+str(iterations)+'.gml'
	nx.write_gml(G, str(name))

	#Indica tamanho da proxima camada
	print(f"Camada {iterations+1} traria: {len(layer_urls)}")

	#Indica numero de pesquisadores visitados
	print(f"#Authors: {len(urls)}")

#Finaliza sessao do navegador
driver.close()
driver.quit()

while True:
	time.sleep(2)
	print('\a')