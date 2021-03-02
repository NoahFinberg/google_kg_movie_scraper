## Movie Google Knowledge Panel Dataset: 1950--2020

We iterate through the Wikipedia list of movies from 1950--2020 and then scrape Google Knowledge Panel for these movies using Apify. The final dataset including the raw html is posted [here](). Feel free to directly explore on [Kaggle](https://www.kaggle.com/noahfinberg/movies)

We use the dataset to estimate the correlation between [average reviews across different platforms](https://github.com/soodoku/mixed_signals).

### Scripts

* [Get Movie List](scripts/get_movie_list.py)
* [Google Knowledge Panel Scraper](scripts/google_kg_scraper.py)
