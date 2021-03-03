###########################################
# Used to scrape Google Knowledge Panel Movie Data
# https://en.wikipedia.org/wiki/Lists_of_American_films
#
# This script primary does two things: (TODO: modularize this a bit better and break into separate files)
# 1. It constructs a Google Search query for a given movie and then calls the Apify Google Scraper API to get the Search Engine Request Page (SERP) for that query
# 2. It identifies and parses the knowledge panel data for a Google SERP and writes that to a csv.
###########################################

from bs4 import BeautifulSoup
import json
import requests
import os
import csv

from dotenv import load_dotenv

load_dotenv() # loads environment variables

### APIFY API ###
GOOGLE_SCRAPER_APIFY_API_KEY = os.getenv('GOOGLE_SCRAPER_APIFY_API_KEY')
GOOGLE_SCRAPER_APIFY_API_ENDPOINT = os.getenv('GOOGLE_SCRAPER_APIFY_API_ENDPOINT')
RUN_GOOGLE_SCRAPE_REQUEST_URL = GOOGLE_SCRAPER_APIFY_API_ENDPOINT + GOOGLE_SCRAPER_APIFY_API_KEY

MONTHS = [
    'JANUARY',
    'FEBRUARY',
    'MARCH',
    'APRIL',
    'MAY',
    'JUNE',
    'JULY',
    'AUGUST',
    'SEPTEMBE',
    'OCTOBER',
    'NOVEMBER',
    'DECEMBER',
]

### Google Scraping ###
def run_apify_google_scraper(RUN_GOOGLE_SCRAPE_REQUEST_URL, query, json_output_file_path, results_per_page=10, max_pages_per_query=1, save_html=True):
    # json input to override default actor input configuration
    input_json = {
        "queries": query, # also takes google search links!! (huge for recursing on people also search for links)
        "resultsPerPage": results_per_page,
        "maxPagesPerQuery": max_pages_per_query,
        "saveHtml": save_html,
        "saveHtmlToKeyValueStore": False,
        "mobileResults": False,
        "includeUnfilteredResults": False
    }

    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

    # Note: APIFY times out after 300 seconds so need to make sure we don't ask for too much in each request...might be able to adjust timeout
    r = requests.post(RUN_GOOGLE_SCRAPE_REQUEST_URL, data=json.dumps(input_json), headers=headers)

    # write output of apify task run to a json file
    with open(json_output_file_path,'w') as f:
        f.write(r.text)

# takes the csv generated from the wikipedia films list and tries to extract the titles
# this is a little tricky because the tables don't have a consistent format from year to year.
# returns a list of movie titles 
def get_titles(movies_list_file_path):
    movies = read_csv(movies_list_file_path)

    # just want movie titles
    titles = []
    for movie in movies:
        movie_parts = movie.split(",")

        # if movie part is just a month remove it
        if any(month in movie_parts[0] for month in MONTHS):
            movie_parts.pop(0)
        
        if movie_parts[0].isdigit() or movie_parts[0].strip() == "L" or movie_parts[0].strip() == "W" or movie_parts[0].strip() == "‡" or movie_parts[0].strip() == "R":
            if movie_parts[1].strip() == "L" or movie_parts[1].strip() == "W" or movie_parts[1].strip() == "‡" or movie_parts[1].strip() == "R":
                title = movie_parts[2]
            else:
                title = movie_parts[1]
        else:
            title = movie_parts[0]
        
        print("____"*80)
        print(movie_parts)
        print(title)

        titles.append(title)

    return titles

# outputs a list of Google search queries to locate the correct movie (format: <movie_title> + 'movie' + <year>)
def generate_google_search_queries(movie_list_file_path, year):
    titles = get_titles(movie_list_file_path)
    queries = [str(title).replace("/"," ") + " movie " + str(year) for title in titles]

    return queries


### PARSERS ###
# returns dictionary will relevant structured data from the knowledge panels
def parse_knowledge_panels(search_results_html, query):
    
    #initialize empty knowledge dict
    knowledge_dict = {}

    soup = BeautifulSoup(search_results_html, 'html.parser')
    # print(soup.title)

    try:
        kp_whole_page_html = soup.find_all("div", class_="kp-wholepage")
        # print(kp_whole_page_html)
    except:
        kp_whole_page_html = ""
    
    try:
        # get title
        title = soup.find_all(attrs={"data-attrid": "title"})[0].get_text()
        # print(title)
    except:
        title = ""

    try:
        # get subtitle
        subtitle = soup.find_all(attrs={"data-attrid": "subtitle"})[0].get_text()

        subtitle_parts = subtitle.split("‧")
        maturity_rating = subtitle_parts[0].split()[0]
        release_year = subtitle_parts[0].split()[1]
        genre = subtitle_parts[1].strip()
        duration = subtitle_parts[2].strip()
    except:
        subtitle = ""
        maturity_rating = ""
        release_year = ""
        genre = ""
        duration = ""

    # print(maturity_rating)
    # print(release_year)
    # print(genre)
    # print(duration)

    try:
        # get title link
        title_link = soup.find_all(attrs={"data-attrid": "title_link"})[0].get("href")
        # print(title_link)
    except:
        title_link = ""

    # get film review ratings
    # "kc:/film/film:reviews"
    IMDb_link = ""
    IMDb_rating = ""
    indie_wire_link = ""
    indie_wire_rating = ""
    rotten_tomatoes_link = ""
    rotten_tomatoes_rating = ""
    meta_critic_link = ""
    meta_critic_rating = ""

    try:
        film_review_ratings = soup.find_all(attrs={"data-attrid": "kc:/film/film:reviews"})[0]
        film_review_ratings_links = film_review_ratings.find_all("a", href=True)

        for link in film_review_ratings_links:
            # print(link.get_text())
            if "IMDb" in link.get_text():
                IMDb_link = link["href"]
                IMDb_rating = link.get_text().replace("IMDb","")
            elif "IndieWire" in link.get_text():
                indie_wire_link = link["href"]
                indie_wire_rating = link.get_text().replace("IndieWire","")
            elif "Rotten Tomatoes" in link.get_text():
                rotten_tomatoes_link = link["href"]
                rotten_tomatoes_rating = link.get_text().replace("Rotten Tomatoes","")
            elif "Metacritic" in link.get_text():
                meta_critic_link = link["href"]
                meta_critic_rating = link.get_text().replace("Metacritic","")
    except:
        pass

    # print(IMDd_link)
    # print(IMDB_rating)
    # print(rotten_tomatoes_link)
    # print(rotten_tomatoes_rating)
    # print(indie_wire_link)
    # print(indie_wire_rating)

    try:
        # get percentage of google users that liked this movie
        # "kc:/ugc:thumbs_up"
        p_google_likes = soup.find_all(attrs={"data-attrid": "kc:/ugc:thumbs_up"})[0].get_text().split()[0]
        # print(p_google_likes)
    except:
        p_google_likes = ""

    try:
        description = soup.find_all(attrs={"data-attrid": "description"})[0].span.get_text().replace("MORE", "")
        # print(description)
    except:
        description = ""

    try:
        # "hw:/collection/films:box office"
        box_office = soup.find_all(attrs={"data-attrid": "hw:/collection/films:box office"})[0].get_text().replace("Box office:", "")
        # print(box_office)
    except:
        box_office = ""
    
    try:
        # "kc:/film/film:theatrical region aware release date"
        release_date = soup.find_all(attrs={"data-attrid": "kc:/film/film:theatrical region aware release date"})[0].get_text().replace("Release date:", "")
        # print(release_date)
    except:
        release_date = ""
    

    try:
        # kc:/film/film:director
        directors = soup.find_all(attrs={"data-attrid": "kc:/film/film:director"})[0].get_text().replace("Directors: ","")
        # print(directors)
    except:
        directors = ""

    try:
        # "kc:/film/film:budget"
        budget = soup.find_all(attrs={"data-attrid": "kc:/film/film:budget"})[0].get_text().replace("Budget:", "")
        # print(budget)
    except:
        budget = ""
    
    try:
        # kc:/award/award_winner:awards
        awards = soup.find_all(attrs={"data-attrid": "kc:/award/award_winner:awards"})[0].get_text().replace("Awards: ", "").replace("MORE", "")
        # print(awards)
    except:
        awards = ""

    #### TODO:  film series, producers ####

    try:
        film_series = soup.find_all(attrs={"data-attrid": "kc:/film/film:film series"})[0].get_text().replace("Film series: ", "")
    except:
        film_series = ""

    try:
        producers = soup.find_all(attrs={"data-attrid": "kc:/film/film:producer"})[0].get_text().replace("Producers: ", "")
    except:
        producers = ""


    try:
        # "kc:/film/film:critic_reviews"
        critic_reviews_html = soup.find_all(attrs={"data-attrid": "kc:/film/film:critic_reviews"})[0]
        # print(critic_reviews_html)
    except:
        critic_reviews_html = ""

    try:
        # audience reviews - includes audience rating summary
        # kc:/ugc:user_reviews
        audience_reviews_html = soup.find_all(attrs={"data-attrid": "kc:/ugc:user_reviews"})[0]
        # print(audience_reviews_html)
    except:
        audience_reviews_html = ""

    

    # fill knowledge_dict
    knowledge_dict["query"] = query
    knowledge_dict["title"] = title
    knowledge_dict["subtitle"] = subtitle
    knowledge_dict["maturity_rating"] = maturity_rating
    knowledge_dict["release_year"] = release_year
    knowledge_dict["genre"] = genre
    knowledge_dict["duration"] = duration
    knowledge_dict["title_link"] = title_link
    knowledge_dict["description"] = description


    knowledge_dict["IMDb_link"] = IMDb_link
    knowledge_dict["IMDb_rating"] = IMDb_rating
    knowledge_dict["rotten_tomatoes_link"] = rotten_tomatoes_link
    knowledge_dict["rotten_tomatoes_rating"] = rotten_tomatoes_rating
    knowledge_dict["meta_critic_link"] = meta_critic_link
    knowledge_dict["meta_critic_rating"] = meta_critic_rating
    knowledge_dict["indie_wire_link"] = indie_wire_link
    knowledge_dict["indie_wire_rating"] = indie_wire_rating
    knowledge_dict["p_google_likes"] = p_google_likes
    
    knowledge_dict["box_office"] = box_office
    knowledge_dict["release_date"] = release_date
    knowledge_dict["directors"] = directors
    knowledge_dict["awards"] = awards
    knowledge_dict["film_series"] = film_series
    knowledge_dict["producers"] = producers
    knowledge_dict["budget"] = budget

    knowledge_dict["critic_reviews_html"] = critic_reviews_html
    knowledge_dict["audience_reviews_html"] = audience_reviews_html
    knowledge_dict["kp_whole_page_html"] = kp_whole_page_html
    
    return knowledge_dict


### FILE HELPERS ###
def read_json_data(file_path):
    with open(file_path) as f:
        search_results_dict = json.load(f)
    return search_results_dict

def read_csv(file_path):
    with open(file_path) as file:
        movies = file.readlines()
        return movies

def write_knowledge_dict_to_csv(knowledge_dict, knowledge_dict_movies_file_path, header_added=True):
    print("writing movie data")

    fieldnames = fieldnames = list(knowledge_dict.keys())


    if not header_added:
        with open(str(knowledge_dict_movies_file_path), 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(fieldnames)
                header_added = True

    with open(str(knowledge_dict_movies_file_path), 'a+', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow(knowledge_dict)


######################################################
### Main Script To Scrape Google Knowledge Panels  ###
######################################################

###
# Part 1. 
# - construct a Google Search query for a given movie
# - then call the Apify Google Scraper API to get the Search Engine Request Page (SERP) for that query
# - one the SERP pages are written to json files, can comment the line that calls Apify to run part two
###

############# Get Google JSON Results ###############
year = 2020 
movies_list_file_path = "data/movie_list/movies_{}.csv".format(year) # read in list of movies from wikipedia
queries = generate_google_search_queries(movies_list_file_path, year) # generate list of google search queries to run

# if retying queries that failed in the pass
# queries =  read_csv("data/failed_queries/failed_queries.csv")

i = 0

for query in queries:
    print("querying: " + query)
    query = query.strip()
    print(query)
    # print(i)
    json_output_file_path = "data/serp_results/{}/{}.json".format(year,query) # where json serp data gets written
    # json_output_file_path = "data/serp_results/failed_queries/{}.json".format(query) # if retrying failed queries

    run_apify_google_scraper(RUN_GOOGLE_SCRAPE_REQUEST_URL, query, json_output_file_path, results_per_page=10, max_pages_per_query=1, save_html=True) # calls the Apify Google Scraper

    ###
    # Part 2. 
    # - parse Google SERP pages for the structured knowledge panel movie data
    # - if the Google SERP page didn't return a knowledge panel, write query to failed queries to try again later
    ###

    # #     ######## PARSE KNOWLEDGE PANEL ###########

    file_path = "data/serp_results/{}/{}.json".format(year, query)
    knowledge_dict_movies_file_path = "data/structured_movie_data/movie_data_{}".format(year)

    # if parsing failed queries
    # file_path = "data/serp_results/failed_queries/{}.json".format(query)
    # knowledge_dict_movies_file_path = "data/structured_movie_data/movie_data_failed_queries.csv"


    # # this will fail sometimes if Apify returned a html - 503 bad gateway error
    try:
        # read google serp file from data folder
        search_results_dict = read_json_data(file_path)

        # parse kg entities
        search_results_html = search_results_dict[0]["html"]
        knowledge_dict = parse_knowledge_panels(search_results_html, query)
        # print(knowledge_dict)

        if i == 0:
            header_added = False
        else:
            header_added = True
        
        # write to csv
        write_knowledge_dict_to_csv(knowledge_dict, knowledge_dict_movies_file_path, header_added)
        # write_knowledge_dict_to_csv(knowledge_dict, knowledge_dict_movies_file_path)
        i = i + 1
    except:
        # if the google serp page didn't return the actual SERP page, write to failed queries to be run later.
        print(query + " failed")
        failed_query_path = "data/failed_queries/failed_queries.csv"
        f = open(failed_query_path,'a+')
        f.write(query + "\n")
        f.close()
        continue

    

   