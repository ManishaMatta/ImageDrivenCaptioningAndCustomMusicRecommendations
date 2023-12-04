import pandas as pd
import nltk
import requests
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
from nltk.corpus import wordnet
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dataProcessing.common import CommonModule

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')

# Configuration variables
CSV_FILE_PATH = 'C:/Users/sushe/Documents/BDA_Fall_2023/Sem1/BDA_696_Python/Project/sample_text.csv'
BASE_URL1 = "https://www.lifewire.com"
BASE_URL2 = "https://www.oberlo.com"
QUOTES_CLASS = "comp mntl-sc-block mntl-sc-block-html"
#QUOTES_CLASS = "my-12 md:px-24"
URL1 = f"{BASE_URL1}/best-instagram-captions-4171697"
URL2 = f"{BASE_URL2}/blog/instagram-captions"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.8",
}
quotes = []

def scrape_quotes_from_website1(url):
    #quotes = []
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        ul_elements = soup.find_all('ul', class_=QUOTES_CLASS)
        for u in ul_elements:
            li_tags = u.find_all('li')
            quotes.extend(li.text for li in li_tags)
    return quotes

def scrape_quotes_from_website2(url):
    #quotes = []
    response = requests.get(url)
    response.status_code
    content = BeautifulSoup(response.text, 'html.parser')
    for i in content.find_all("li", style="font-weight: 400;"):
        #print(i.get_text())
        quotes.append(i.get_text())
    return quotes

def get_next_page_url(soup):
    next_page_url = soup.find('a', class_='next_page')
    if next_page_url:
        return next_page_url['href']
    else:
        return None

def scrape_quotes_from_whole_website():
    url = "https://www.goodreads.com/quotes/tag/free?page="
    while True:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        quote_container = soup.find_all('div', class_='quote')
        for quote in quote_container:
            text = quote.find('div', class_='quoteText').text.strip()
            quotes.append(text)
        next_page_url = get_next_page_url(soup)
        if not next_page_url:
            break
        else:
            url = "https://www.goodreads.com" + next_page_url
    return quotes

def process_and_print_quotes(quotes, text_data):
    for line in text_data:
        if isinstance(line, str):
            sentences = sent_tokenize(line)
            for sentence in sentences:
                words = [word for word, tag in pos_tag(word_tokenize(sentence)) if tag.startswith(('VB', 'NN', 'JJ'))]
                print(' '.join(words) + ":")
                print('\n')
                keyword_list = words
                synonyms = []
                for word in keyword_list:
                    for syn in wordnet.synsets(word):
                        for lm in syn.lemmas():
                            synonyms.append(lm.name())
                print(synonyms)
                print('\n')
                matching_quotes = [quote for quote in quotes if any(keyword in quote for keyword in synonyms)]
                for quote in matching_quotes:
                    print(quote)
                print('\n')
    for i in text_data:
        val = []
        for j in matching_quotes:
            cosine_sim = CommonModule.similarity_score(i.strip(), j.strip())
            val.append((cosine_sim, j.strip(), i.strip()))
        sorted_val_desc = sorted(val, key=lambda x: x[0], reverse=True)
        print(sorted_val_desc[:3])


def main():
    txt_df = pd.read_csv(CSV_FILE_PATH, sep='|')
    txt_dt = txt_df[' comment'].head(1)
    print(txt_dt)
    print('\n')

    quotes = scrape_quotes_from_website1(URL1)#scrape from lifewire website
    quotes = scrape_quotes_from_website2(URL2)#scrape from oberlo website
    quotes = scrape_quotes_from_whole_website()

    print("Quotes scraped:", len(quotes))  # Add this to check if quotes were scraped
    print('\n')

    process_and_print_quotes(quotes, txt_dt)

if __name__ == "__main__":
    main()