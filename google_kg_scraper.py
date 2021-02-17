# pyenv activate google-kg-utility-3.6.5 
from bs4 import BeautifulSoup
import json
import requests
import os
import csv

from dotenv import load_dotenv

load_dotenv() # loads environment variables
GOOGLE_SCRAPER_APIFY_API_KEY = os.getenv('GOOGLE_SCRAPER_APIFY_API_KEY')

### APIFY API ###

# # Runs this actor task and waits for its finish. 
# # Optionally, the POST payload can contain a JSON object whose fields override the actor input configuration. 
# # The HTTP response contains the actor's dataset items, while the format of items depends on specifying dataset items' format parameter. 
# # Beware that the HTTP connection might time out for long-running actors.
RUN_GOOGLE_SCRAPE_REQUEST_URL = "https://api.apify.com/v2/actor-tasks/eIv7L8YPtSufwUJQd/run-sync-get-dataset-items?token=" + GOOGLE_SCRAPER_APIFY_API_KEY


# Takes a URL that hits our google scraper apify API endpoint.
# Also takes different config options for the scraper. Most important is the queries that we pass in
# pro tip: if we don't care about knowledge panel information, setting save_html to False will likely speed up the query a bit
# we generally want to keep max pages per query at 1 as going to subsequent pages gets slower for each page...instead if we want a lot of results we can set the results per page up as high as 100
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


def read_json_data(file_path):
    # Parse playlists, for each playlist write video and comment data to playlists folder
    with open(file_path) as f:
        search_results_dict = json.load(f)
    return search_results_dict

# returns dictionary will all the structured data from the knowledge panels and additional queries to search
def parse_knowledge_panels(search_results_html):
    
    #initialize empty knowledge dict
    knowledge_dict = {}

    soup = BeautifulSoup(search_results_html, 'html.parser')
    # print(soup.title)

    kp_whole_page_html = soup.find_all("div", class_="kp-wholepage")
    # print(kp_whole_page_html)

    # get title
    title = soup.find_all(attrs={"data-attrid": "title"})[0].get_text()
    print(title)

    # get subtitle
    subtitle = soup.find_all(attrs={"data-attrid": "subtitle"})[0].get_text()
    # print(subtitle)

    # get title link
    title_link = soup.find_all(attrs={"data-attrid": "title_link"})[0].get("href")
    # print(title_link)

    # get film review ratings
    # "kc:/film/film:reviews"
    film_review_ratings = soup.find_all(attrs={"data-attrid": "kc:/film/film:reviews"})[0]
    film_review_ratings_links = film_review_ratings.find_all("a", href=True)
    IMDb_link = ""
    IMDb_rating = ""
    indie_wire_link = ""
    indie_wire_rating = ""
    rotten_tomatoes_link = ""
    rotten_tomatoes_rating = ""

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

    # print(IMDd_link)
    # print(IMDB_rating)
    # print(rotten_tomatoes_link)
    # print(rotten_tomatoes_rating)
    # print(indie_wire_link)
    # print(indie_wire_rating)

    # get percentage of google users that liked this movie
    # "kc:/ugc:thumbs_up"
    p_google_likes = soup.find_all(attrs={"data-attrid": "kc:/ugc:thumbs_up"})[0].get_text().split()[0]
    # print(p_google_likes)

    description = soup.find_all(attrs={"data-attrid": "description"})[0].span.get_text().replace("MORE", "")
    # print(description)

    # "hw:/collection/films:box office"
    box_office = soup.find_all(attrs={"data-attrid": "hw:/collection/films:box office"})[0].get_text().replace("Box office:", "")
    # print(box_office)

    # "kc:/film/film:theatrical region aware release date"
    release_date = soup.find_all(attrs={"data-attrid": "kc:/film/film:theatrical region aware release date"})[0].get_text().replace("Release date:", "")
    # print(release_date)

    # "kc:/film/film:budget"
    budget = soup.find_all(attrs={"data-attrid": "kc:/film/film:budget"})[0].get_text().replace("Budget:", "")
    # print(budget)


    # "kc:/film/film:critic_reviews"
    critic_reviews_html = soup.find_all(attrs={"data-attrid": "kc:/film/film:critic_reviews"})[0]
    # print(critic_reviews_html)


    # audience reviews - includs audience rating summary
    # kc:/ugc:user_reviews
    audience_reviews_html = soup.find_all(attrs={"data-attrid": "kc:/ugc:user_reviews"})[0]
    # print(audience_reviews_html)

    # fill knowledge_dict
    knowledge_dict["title"] = title
    knowledge_dict["subtitle"] = subtitle
    knowledge_dict["title_link"] = title_link
    knowledge_dict["description"] = description

    knowledge_dict["IMDb_link"] = IMDb_link
    knowledge_dict["IMDb_rating"] = IMDb_rating
    knowledge_dict["rotten_tomatoes_link"] = rotten_tomatoes_link
    knowledge_dict["rotten_tomatoes_rating"] = rotten_tomatoes_rating
    knowledge_dict["indie_wire_link"] = indie_wire_link
    knowledge_dict["indie_wire_rating"] = indie_wire_rating
    knowledge_dict["p_google_likes"] = p_google_likes
    
    knowledge_dict["box_office"] = box_office
    knowledge_dict["release_date"] = release_date
    knowledge_dict["budget"] = budget

    knowledge_dict["critic_reviews_html"] = critic_reviews_html
    knowledge_dict["audience_reviews_html"] = audience_reviews_html
    knowledge_dict["kp_whole_page_html"] = kp_whole_page_html
    
    return knowledge_dict


def write_knowledge_dict_to_csv(knowledge_dict, knowledge_dict_movies_file_path):
    # nodes
    print("writing movie data")
    print(knowledge_dict)
    with open(str(knowledge_dict_movies_file_path), 'a+', newline='') as csvfile:
        fieldnames = ['title','subtitle', 'title_link', 'description',
                    'IMDb_link','IMDb_rating', 'rotten_tomatoes_link','rotten_tomatoes_rating','indie_wire_link','indie_wire_rating','p_google_likes',
                    'box_office', 'release_date', 'budget',
                    'critic_reviews_html', 'audience_reviews_html', 'kp_whole_page_html']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({'title': knowledge_dict['title'], 'subtitle': knowledge_dict['subtitle'], 'title_link': knowledge_dict['title_link'], 'description': knowledge_dict["description"],
                        'IMDb_link': knowledge_dict['IMDb_link'], 'IMDb_rating': knowledge_dict['IMDb_rating'],
                        'rotten_tomatoes_link': knowledge_dict['rotten_tomatoes_link'], 'rotten_tomatoes_rating': knowledge_dict['rotten_tomatoes_rating'],
                        'indie_wire_link': knowledge_dict['indie_wire_link'], 'indie_wire_rating': knowledge_dict['indie_wire_rating'],
                        'p_google_likes': knowledge_dict['p_google_likes'], 'box_office': knowledge_dict['box_office'], 'release_date': knowledge_dict['release_date'], 'budget': knowledge_dict['budget'],
                        'critic_reviews_html': knowledge_dict['critic_reviews_html'],'audience_reviews_html': knowledge_dict['audience_reviews_html'], 'kp_whole_page_html': knowledge_dict['kp_whole_page_html']})


############# Get Google JSON Results ###############

# query = "Avengers: Endgame"
# json_output_file_path = "data/{}.json".format(query)

# run_apify_google_scraper(RUN_GOOGLE_SCRAPE_REQUEST_URL, query, json_output_file_path, results_per_page=10, max_pages_per_query=1, save_html=True)


######## PARSE KNOWLEDGE PANEL ###########

file_path = "data/Avengers: Endgame.json"
knowledge_dict_movies_file_path = "data/movie_results/mixed_signals.csv"

# read google serp file from data folder
search_results_dict = read_json_data(file_path)

# parse kg entities
search_results_html = search_results_dict[0]["html"]
knowledge_dict = parse_knowledge_panels(search_results_html)
print(knowledge_dict)


# write to csv
write_knowledge_dict_to_csv(knowledge_dict, knowledge_dict_movies_file_path)



### OTHER DATA - not relevant rn

# def parse_organic_results(data):
#     organic_results = data["organicResults"]
#     return organic_results

# def parse_related_queries(data):
#     related_queries = data["relatedQueries"]
#     return related_queries

# def parse_paid_results(data):
#     paid_results = data["paidResults"]
#     return paid_results

# def parse_paid_products(data):
#     paid_products = data["paidProducts"]
#     return paid_products

# def parse_people_also_ask(data):
#     people_also_ask = data["peopleAlsoAsk"]
#     return people_also_ask


# #### FILE HELPERS #####

# # read input labels, returns list of lables
# def read_queries_from_txt(google_queries_file_path):
#     with open(google_queries_file_path) as file:
#         queries = file.readlines()
#         return queries


# def write_organic_results_to_txt(organic_results, file_path):
#     with open(file_path, 'w') as f:
#         for url in organic_results:
#             f.write("%s\n" % url)

# def write_new_query_to_txt(new_query, file_path):
#     with open(file_path, 'a+') as f:
#         f.write("%s\n" % new_query)



    
#     # edges

#     label = knowledge_dict["label"]
    
#     if knowledge_dict["ceo"] != "":
#         with open(str(knowledge_dict_edges_file_path), 'a+', newline='') as csvfile:
#             fieldnames = ['source_name','property', 'target_name']
#             writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#             writer.writerow({'source_name': knowledge_dict["ceo"], 'property': "employee of", 'target_name': label })
    
#     if len(knowledge_dict["founders"]) > 0:
#         founders = knowledge_dict["founders"] 
#         for founder in founders:
#             with open(str(knowledge_dict_edges_file_path), 'a+', newline='') as csvfile:
#                 fieldnames = ['source_name','property', 'target_name']
#                 writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#                 writer.writerow({'source_name': label, 'property': "founded by", 'target_name': founder })

#     if len(knowledge_dict["products"]) > 0:
#         products = knowledge_dict["products"] 
#         for product in products:
#             with open(str(knowledge_dict_edges_file_path), 'a+', newline='') as csvfile:
#                 fieldnames = ['source_name','property', 'target_name']
#                 writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#                 writer.writerow({'source_name': product, 'property': "product of", 'target_name': label })

#     if knowledge_dict["parent_organization"] != "":
#         parent_organization = knowledge_dict["parent_organization"]
#         with open(str(knowledge_dict_edges_file_path), 'a+', newline='') as csvfile:
#             fieldnames = ['source_name','property', 'target_name']
#             writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#             writer.writerow({'source_name': label, 'property': "subsidiary of", 'target_name': parent_organization })

#     if len(knowledge_dict["subsidiaries"]) > 0:
#         subsidiaries = knowledge_dict["subsidiaries"] 
#         for subsidiary in subsidiaries:
#             subsidiary = dequote(subsidiary)
#             with open(str(knowledge_dict_edges_file_path), 'a+', newline='') as csvfile:
#                 fieldnames = ['source_name','property', 'target_name']
#                 writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#                 writer.writerow({'source_name': subsidiary, 'property': "subsidiary of", 'target_name': label })

    
# def dequote(s):
#     """
#     If a string has single or double quotes around it, remove them.
#     Make sure the pair of quotes match.
#     If a matching pair of quotes is not found, return the string unchanged.
#     """
#     if (s[0] == s[-1]) and s.startswith(("'", '"')):
#         return s[1:-1]
#     return s


# ### Google Knowledge Panel Structured Data ###

# # General Company Search: Honeywell or schneider electric company

# #  kc
# # data-attrid="kc:/organization/organization:headquarters"
# # data-attrid="kc:/organization/organization:ceo"


# # data-attrid="kc:/business/issuer:stock quote"
# # data-attrid="kc:/organization/organization:customer service phone"
# # data-attrid="kc:/business/business_operation:company_products_and_refinements"
# # data-attrid="kc:/business/issuer:sideways" # people also search for


# # data-attrid="kc:/ugc:facts" 
# # data-attrid="kc:/business/business_operation:founder
# # data-attrid="kc:/organization/organization:founded"
# # data-attrid="kc:/common/topic:social media presence"
# # data-attrid="kc:/automotive/company:model years"


# # hw
# # hw:/collection/organizations:headquarters location
# # data-attrid="hw:/collection/organizations:revenue"
# # data-attrid="hw:/collection/organizations:subsidiaries"
# # data-attrid="hw:/collection/organizations:coo"
# # data-attrid="hw:/collection/organizations:type"
# # data-attrid="hw:/collection/organizations:parent"


# # okra
# # data-attrid="okra/answer_panel/Competitors"
# # data-attrid="okra/answer_panel/Mission statement"
# # data-attrid="okra/answer_panel/Salary"
# # data-attrid="okra/answer_panel/Core values"
# # data-attrid="okra/answer_panel/Ipo"
# # data-attrid="okra/answer_panel/Battery life"
# # data-attrid="okra/answer_panel/Making"
# # data-attrid="okra/answer_panel/History"
# # data-attrid="okra/answer_panel/Dividend"
# # data-attrid="okra/answer_panel/Slogan"
# # data-attrid="okra/answer_panel/Ownership"
# # data-attrid="okra/answer_panel/Bailout"
# # data-attrid="okra/answer_panel/Tesla merger"


# # ss
# # data-attrid="ss:/webfacts:locat"
# # data-attrid="ss:/webfacts:product_output"
# # data-attrid="ss:/webfacts:divis"
# # data-attrid="ss:/webfacts:number_of_locat"
# # data-attrid="ss:/webfacts:former"

# # other
# # data-attrid="visit_official_site"

# ## Knowledge Panel Links

# # NOTE: Can recurse on these...

# # subsidaries
# # data-attrid="hw:/collection/organizations:subsidiaries" [DIV]
# # <a class="fl" href="/search?sxsrf=ALeKk02mwYUTrSRic9RdNbRX-yDTWEOE5A:1609880774643&amp;q=honeywell+subsidiaries&amp;stick=H4sIAAAAAAAAAOPgE-LUz9U3MEyvMDPT0swot9JPzs_JSU0uyczP088vSk_My6xKBHGKrYpLk4ozUzITizJTixeximXk56VWlqfm5CggSwAAYf2RUVEAAAA&amp;sa=X&amp;ved=2ahUKEwjy7M-d2YXuAhUNm-AKHeJxAKUQ44YBKAMwIHoECCwQBQ"><span class="SW5pqf">MORE</span></a> # look for href in link with MORE as text

# # people also search for
# # <a class="EbH0bb" href="/search?biw=1039&amp;bih=666&amp;sxsrf=ALeKk01OFLRdMMJzJeVazJ7hPezZSsiW1Q:1609883281552&amp;q=Honeywell&amp;stick=H4sIAAAAAAAAAONgFuLUz9U3MEyvMDNTQjC1ZLKTrfSTSosz81KLi_Uzi4tLU4usijNTUssTK4sXsXJ65OelVpan5uTsYGUEAEKND8xFAAAA&amp;sa=X&amp;ved=2ahUKEwi2rYHJ4oXuAhUESN8KHfM6C6IQzTooATAregQIJBAC"><span class="rhsg3">View 15+ more</span></a>


# # Product search: Honeywell Products
# # Maybe we want to scrape google shopping?

# # Knowledge Panel (People)

# # data-attrid="kc:/people/person:born"
# # data-attrid="kc:/people/person:spouse"
# # data-attrid="kc:/people/person:parents"
# # data-attrid="hw:/collection/organization_founders:founded organization"
# # data-attrid="kc:/people/person:education"



# # data-attrid="kc:/book/author:books only"
# # data-attrid="ss:/webfacts:net_worth"
# # data-attrid="kc:/people/person:children"
# # data-attrid="kc:/people/person:movies"
# # data-attrid="kc:/people/deceased_person:died"
# # data-attrid="kc:/people/person:quote"

# # Knowledge Panel (Products)


# ## alot of extensions here



# #######################
# ### QUERY GENERATOR ###
# #######################