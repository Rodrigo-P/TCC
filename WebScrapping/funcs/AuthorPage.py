from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

def add_author(web_driver, author_id, author_graph):
	author_data = get_author_data(web_driver, author_id) #Dados do autor

	if(author_id not in author_graph.nodes()): #Adiciona, caso o pesquisador seja novo no grafo
		author_graph.add_node(author_id, attr = author_data)
	else: #Adiciona atributos se autor já estava no grafo
		for attribute in author_data:
			author_graph.nodes[author_id][attribute] = author_data[attribute]

def get_article_urls(web_driver):
	article_url_list = []

	article_list = web_driver.find_elements(By.CSS_SELECTOR, "li[class='results-list-item']")
	for article in article_list:
		if(article.find_element(By.CSS_SELECTOR, "span").get_attribute('innerText').startswith("Article")): #Checa se documento é artigo
			article_url_list.append(article.find_element(By.CSS_SELECTOR, "a[href]").get_attribute("href"))

	return article_url_list

def get_author_articles(web_driver, sleep_time = 5):
	article_url_list = get_article_urls(web_driver)
	next_button = web_driver.find_element(By.XPATH,"//span[text()='Next']").find_element(By.XPATH, "./..") #Finds Next Span, gets parent button

	while(next_button.is_enabled()):
		web_driver.execute_script("arguments[0].scrollIntoView();", next_button)
		web_driver.execute_script("arguments[0].click();", next_button)
		time.sleep(sleep_time)
		article_url_list += get_article_urls(web_driver)
		next_button = web_driver.find_element(By.XPATH,"//span[text()='Next']").find_element(By.XPATH, "./..") #Finds Next Span, gets parent button

	return article_url_list

def get_author_data(web_driver, scopus_id):
	author_soup = BeautifulSoup(web_driver.page_source,'lxml')
	web_driver.find_element(By.ID, "AuthorHeader__showAllAuthorInfo").click() #Abrir aba de dados
	time.sleep(0.5)
	sidebar_soup = BeautifulSoup(web_driver.page_source, 'lxml')
	web_driver.find_element(By.CSS_SELECTOR, "button[data-test-id='flyout-close-button']").click() #Fecha aba de dados

	author_information = {"ID": scopus_id}

	name = author_soup.find("title").string[:-26]
	author_information["Name"] = name

	author_location = author_soup.find("span", {"data-testid": "authorInstitution"})
	found_elements = author_location.find_all("span")

	author_information["Institution"] = found_elements[0].string

	location = found_elements[1].string[2:].split(sep = ",")
	author_information["Country"] = location[1].strip()
	author_information["City"] = location[0]

	found_elements = author_soup.find_all("span", {"data-testid": "unclickable-count"})
	author_information["Citations"] = found_elements[0].string
	author_information["Documents"] = found_elements[1].string
	author_information["hIndex"] = found_elements[2].string

	author_areas = sidebar_soup.find("span", {"data-testid": "authorSubjects"}).string.split(sep = " • ")
	author_information["Areas"] = author_areas

	return author_information