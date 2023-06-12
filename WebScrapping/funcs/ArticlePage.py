from selenium.webdriver.common.by import By
import time

def add_article_without_next_layer(web_driver, explored_ids, author_graph, author_id):
	#Lista de autores do artigo
	coauthor_id_list = get_author_id_list(web_driver)

	for coauthor_id in coauthor_id_list:
		#Ignora pesquisadores já explorados
		if(coauthor_id in explored_ids):
			continue

		#Adiciona, caso o pesquisador seja novo no grafo
		if(coauthor_id not in author_graph.nodes()):
			author_graph.add_node(coauthor_id)
		
		#Aumenta o peso se ja houver uma conexao
		if author_graph.has_edge(author_id, coauthor_id):
			author_graph[author_id][coauthor_id]['weight'] += 1
		#Cria conexao de peso 1, se nao existir uma
		else:
			author_graph.add_edge(author_id, coauthor_id, weight=1)

def add_article(web_driver, explored_ids, next_layer, author_graph, author_id):
	#Lista de autores do artigo
	coauthor_id_list = get_author_id_list(web_driver)

	for coauthor_id in coauthor_id_list:
		#Ignora pesquisadores já explorados
		if(coauthor_id in explored_ids):
			continue

		#Adiciona coautor à lista de próximos autores
		next_layer.add(coauthor_id)

		#Adiciona, caso o pesquisador seja novo no grafo
		if(coauthor_id not in author_graph.nodes()):
			author_graph.add_node(coauthor_id)
		
		#Aumenta o peso se ja houver uma conexao
		if author_graph.has_edge(author_id, coauthor_id):
			author_graph[author_id][coauthor_id]['weight'] += 1
		#Cria conexao de peso 1, se nao existir uma
		else:
			author_graph.add_edge(author_id, coauthor_id, weight=1)

def get_author_id(web_driver, author_buttons, author_num):
	author_buttons[author_num].click() #First Author
	author_link = web_driver.find_element(By.XPATH,"//span[text()='View full profile']").find_element(By.XPATH, "./..").get_attribute("href") #Get link to author from tab
	print(author_link[author_link.find("Id=")+3 : author_link.find("&origin")])
	web_driver.find_element(By.CSS_SELECTOR, "button[data-test-id='flyout-close-button']").click() #Fecha aba de dados

	return author_link[author_link.find("Id=")+3 : author_link.find("&origin")]

def get_author_id_list(web_driver):
	div_with_authors = web_driver.find_element(By.CSS_SELECTOR, "div[class='row'] [data-testid='author-list']") #Container de botões
	author_buttons = div_with_authors.find_elements(By.CSS_SELECTOR, "button")[:-1] #Lista de botões

	#Check if author list is expandable
	if(author_buttons[-1].find_element(By.CSS_SELECTOR, "span").get_attribute('innerText') == "Show additional authors"):
		# author_buttons[-1].click() #Expand author list, makes buttons interactable
		web_driver.execute_script("arguments[0].scrollIntoView();", author_buttons[-1])
		web_driver.execute_script("arguments[0].click();", author_buttons[-1])
		author_buttons.pop() #Remove expand button from list
	id_list = []
	time.sleep(0.2)
	
	for author_num in range(len(author_buttons)):
		# author_buttons[author_num].click() #Open author tab
		web_driver.execute_script("arguments[0].scrollIntoView();", author_buttons[author_num])
		web_driver.execute_script("arguments[0].click();", author_buttons[author_num])

		time.sleep(0.2)
		author_link = web_driver.find_element(By.XPATH,"//span[text()='View full profile']").find_element(By.XPATH, "./..").get_attribute("href") #Get link to author from tab
		close_button = web_driver.find_element(By.CSS_SELECTOR, "button[data-test-id='flyout-close-button']") #Close tab
		web_driver.execute_script("arguments[0].scrollIntoView();", close_button)
		web_driver.execute_script("arguments[0].click();", close_button)

		id_list.append(int(author_link[author_link.find("Id=")+3 : author_link.find("&origin")]))#Append author ID
		time.sleep(0.2)
	return id_list