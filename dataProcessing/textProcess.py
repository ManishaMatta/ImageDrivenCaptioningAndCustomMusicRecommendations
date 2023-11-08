import pandas as pd
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
from nltk.corpus import wordnet
import requests
from bs4 import BeautifulSoup
import random
import re

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')  # Ensure wordnet data is downloaded

url = "https://www.goodreads.com/quotes/tag/free?page="
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.8",
}

def get_synonyms(word):
    synonyms = []
    for syn in wordnet.synsets(word):
        for lm in syn.lemmas():
            synonyms.append(lm.name())
    return set(synonyms)

def fetch_data(url, headers):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup

def get_next_page_url(soup):
    next_page_url = soup.find('a', class_='next_page')
    if next_page_url:
        return next_page_url['href']
    else:
        return None

def extract_quotes(soup):
    quotes = []
    quote_container = soup.find_all('div', class_='quote')

    for quote in quote_container:
        text = quote.find('div', class_='quoteText').text.strip()
        quotes.append(text)
    return quotes

def generate_caption(quotes, synonyms):
    quote = random.choice(quotes)
    keyword = random.choice(synonyms)
    caption = f"{quote}"
    return caption

def scrape_quotes_from_whole_website():
    quotes = []
    url = "https://www.goodreads.com/quotes/tag/free?page="
    while True:
        soup = fetch_data(url, headers)
        quotes += extract_quotes(soup)

        next_page_url = get_next_page_url(soup)
        if not next_page_url:
            break
        else:
            url = "https://www.goodreads.com" + next_page_url
    return quotes

if __name__ == "__main__":
    txt_df = pd.read_csv('C:/Users/sushe/Documents/BDA_Fall_2023/Sem1/BDA_696_Python/Project/results.csv', sep='|')
    print(txt_df[' comment'])

    synonyms = set()  # Initialize synonyms as a set
    for line in txt_df[' comment']:
        if isinstance(line, str):  # Check if it's a string
            for ln in sent_tokenize(line):
                wordtokens = word_tokenize(ln)
                tag_word = pos_tag(wordtokens)
                filtered_words = list(filter(lambda word: word[1].startswith('VB') or word[1].startswith('NN') or word[1].startswith('JJ'), tag_word))
                words = [item[0] for item in filtered_words]
                print(' '.join(words) + ":")
                print("\n")
                quotes = scrape_quotes_from_whole_website()
                keyword_list = words
                result = [any(k in q for k in keyword_list) for q in quotes]
                for res, quote in zip(result, quotes):
                    if res:
                        print(quote)

    '''result = [all(k in q for k in keyword_list) for q in quotes]
    for res, str in zip(result, quotes):
        if res:
            print(str)
        else:
            print("No Quotes Available")'''


