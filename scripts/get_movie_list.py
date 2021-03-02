# Scrape Wikipedia list of American films for the last 50 years
# https://en.wikipedia.org/wiki/Lists_of_American_films

# pyenv activate google-kg-utility-3.6.5 
from bs4 import BeautifulSoup
import json
import requests
import os
import csv


# 1. get wikipedia pages
def get_wikipedia_film_list_urls():
    wikipedia_film_list_urls = {}
    wikipedia_american_film_list_url = "https://en.wikipedia.org/wiki/List_of_American_films_of_"
    
    # populate wikipedia film list urls
    for year in range(1950, 2020):
        wikipedia_film_list_urls[year] = wikipedia_american_film_list_url + str(year)

    return wikipedia_film_list_urls


# 2. parse wikitables for movie info

# takes an html table and converts it to a list of dicts
def html_table_to_list_of_dicts(table):
    data = []

    rows = table.find_all("tr")
    
    thead = table.find_all("th")

    thead = [th.get_text().strip() for th in thead ]

    for row in rows:
        cells = row.find_all("td")

        try:
            item_dict = {}
            for i, cell in enumerate(cells):
                item_dict[thead[i]] = cell.text.strip()
            
            data.append(item_dict)
        except:
            continue
    return data
   


def parse_wiki_table_for_movie_data(wiki_film_list_url):
    movie_data = []

    wiki_page = requests.get(wiki_film_list_url)
    soup = BeautifulSoup(wiki_page.text, 'html.parser')

    wikitables = soup.find_all("table", class_="wikitable")

    for wikitable in wikitables:
        movies = html_table_to_list_of_dicts(wikitable)
        movie_data = movie_data + movies

    return movie_data



# 3. write movie data to csv

def write_movie_data_to_csv(movie_dict):
    pass

def write_movie_data_to_csv(movie_dict, movie_dict_file_path):
    print("writing movie data")
    print(movie_dict)
    with open(str(movie_dict_file_path), 'a+', newline='') as csvfile:

        fieldnames = list(movie_dict.keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow(movie_dict)

year = 2020
### DO WORK ###
movie_dict_file_path = "data/movie_list/movies_{}.csv".format(year)
# for year in range(1950, 2021):


# 1. get film urls for each year
wikipedia_american_film_list_url = "https://en.wikipedia.org/wiki/List_of_American_films_of_"
wiki_film_url = wikipedia_american_film_list_url + str(year)

# 2. parse movie tables on wikipedia movie list page
movies = parse_wiki_table_for_movie_data(wiki_film_url)

# 3. write move data to csv
for movie in movies:
    if bool(movie):
        write_movie_data_to_csv(movie, movie_dict_file_path)
