## Movie Google Knowledge Panel Dataset: 1950--2020

We iterate through the Wikipedia list of movies from 1950--2020 and then scrape Google Knowledge Panel for these movies using [Apify's Google Search Results Scraper](https://apify.com/apify/google-search-scraper). The final dataset including the raw html of the SERP pages as well as the parsed Knowledge Panels is posted [here on Harvard Dataverse](https://dataverse.harvard.edu/dataverse/americanmovies). Feel free to directly explore on [Kaggle](https://www.kaggle.com/noahfinberg/movies) too.

We use the dataset to estimate the correlation between [average reviews across different platforms](https://github.com/soodoku/mixed_signals).

### Scripts

* [Get Movie List](scripts/get_movie_list.py)
* [Google Knowledge Panel Scraper](scripts/google_kg_scraper.py)

### Future
- It'd be nice (and not super difficult) to generalize this code to be able to automatically parse any google knowledge panel beyond movies for all of the structured data.

### Authors 
Noah Finberg and Gaurav Sood