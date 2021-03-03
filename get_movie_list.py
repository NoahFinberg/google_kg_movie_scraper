###########################################
# Used to scrape Wikipedia list of American films for the last 50 years
# https://en.wikipedia.org/wiki/Lists_of_American_films
#
# This script generates a csv that lists all American movies included on the wikipedia page for a given year (e.g. https://en.wikipedia.org/wiki/List_of_American_films_of_2020)
###########################################

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

# write list of movies to csv
def write_movie_data_to_csv(movie_dict, movie_dict_file_path):
    print("writing movie data")
    print(movie_dict)
    with open(str(movie_dict_file_path), 'a+', newline='') as csvfile:

        fieldnames = list(movie_dict.keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow(movie_dict)



##############################################################
### Main Script To Generate List of Movies From Wikipedia  ###
##############################################################

year = 2020 # using 2020 and an example year, but can loop through all years 1950-2020
movie_dict_file_path = "data/movie_list/movies_{}.csv".format(year) # output file to write list of movies from wikipedia list of films page (e.g. https://en.wikipedia.org/wiki/List_of_American_films_of_2020)

# 1. construct the wikipedia film list url
wikipedia_american_film_list_url = "https://en.wikipedia.org/wiki/List_of_American_films_of_"
wiki_film_url = wikipedia_american_film_list_url + str(year)

# 2. parse movie tables on wikipedia movie list page
movies = parse_wiki_table_for_movie_data(wiki_film_url)

# 3. write list of movie data to csv for the specified year
for movie in movies:
    if bool(movie):
        write_movie_data_to_csv(movie, movie_dict_file_path)
