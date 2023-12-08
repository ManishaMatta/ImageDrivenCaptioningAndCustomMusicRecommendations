import pandas as pd
import nltk
import requests
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
from nltk.corpus import wordnet
from common import CommonModule

# nltk.download('punkt')
# nltk.download('averaged_perceptron_tagger')
# nltk.download('wordnet')

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
quotes1 = []

class TextModule:
    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def scrape_quotes_from_website2(url):
        #quotes = []
        response = requests.get(url)
        response.status_code
        content = BeautifulSoup(response.text, 'html.parser')
        for i in content.find_all("li", style="font-weight: 400;"):
            #print(i.get_text())
            quotes.append(i.get_text())
        return quotes

    @staticmethod
    def get_next_page_url(soup):
        next_page_url = soup.find('a', class_='next_page')
        if next_page_url:
            return next_page_url['href']
        else:
            return None

    @staticmethod
    def scrape_quotes_from_whole_website():
        url = "https://www.goodreads.com/quotes/tag/free?page="
        while True:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            quote_container = soup.find_all('div', class_='quote')
            for quote in quote_container:
                text = quote.find('div', class_='quoteText').text.strip()
                quotes1.append(text)
            next_page_url = TextModule.get_next_page_url(soup)
            if not next_page_url:
                break
            else:
                url = "https://www.goodreads.com" + next_page_url
        return quotes1

    @staticmethod
    def process_and_print_quotes(quotes, text_data):
        for line in text_data:
            if isinstance(line, str):
                sentences = sent_tokenize(line)
                for sentence in set(sentences):
                    words = [word for word, tag in pos_tag(word_tokenize(sentence)) if tag.startswith(('VB', 'NN', 'JJ'))]
                    # print(' '.join(words) + ":")
                    # print('\n')
                    keyword_list = words
                    synonyms = []
                    for word in keyword_list:
                        for syn in wordnet.synsets(word):
                            for lm in syn.lemmas():
                                synonyms.append(lm.name())
                    #print(synonyms)
                    #print('\n')
                    matching_quotes = [quote for quote in quotes if any(keyword in quote for keyword in synonyms)]
                    #for quote in matching_quotes:
                    #print(quote)
                    #print('\n')
        for i in text_data:
            val = []
            for j in matching_quotes:
                cosine_sim = CommonModule.similarity_score(i.strip(), j.strip())
                val.append((cosine_sim, j.strip(), i.strip()))
            sorted_val_desc = sorted(val, key=lambda x: x[0], reverse=True)
        return [i[1] for i in sorted_val_desc[:3]]


def text_process(caption):
    # txt_df = pd.read_csv(CSV_FILE_PATH, sep='|')
    # txt_dt = txt_df[' comment'].head(1)
    # print(txt_dt)
    # print('\n')
    caption = caption.replace('startseq','')

    '''quotes = scrape_quotes_from_website1(URL1)#scrape from lifewire website
    quotes = scrape_quotes_from_website2(URL2)#scrape from oberlo website
    quotes1 = scrape_quotes_from_whole_website()'''

    '''df_quotes = pd.DataFrame({'Quotes': quotes})
    df_quotes1 = pd.DataFrame({'Quotes': quotes1})

    output_file_path = "C:/Users/sushe/Documents/BDA_Fall_2023/quotes_output1.csv"
    df_quotes.to_csv(output_file_path, sep='|', header=True, index=False)

    output_file_path1 = "C:/Users/sushe/Documents/BDA_Fall_2023/quotes_output2.csv"
    df_quotes1.to_csv(output_file_path1, sep='|', header=True, index=False)'''

    fquotes = pd.read_csv("/Users/Manisha/Documents/MS/SDSU/course/BDA-696/final_project/project/ImageDrivenCaptioningAndCustomMusicRecommendations/resources/datasets/quotes_output1.csv", sep='|', header='infer',skipinitialspace=True)
    fquotes_dt = fquotes['Quotes']
    fquotes1 = pd.read_csv("/Users/Manisha/Documents/MS/SDSU/course/BDA-696/final_project/project/ImageDrivenCaptioningAndCustomMusicRecommendations/resources/datasets/quotes_output2.csv", sep='|', header='infer',skipinitialspace=True)
    fquotes_dt1 = fquotes1['Quotes']

    # print("Quotes scraped:", len(fquotes_dt))  # Add this to check if quotes were scraped
    # print("Quotes scraped:", len(fquotes_dt1))
    # print('\n')
    text_captions = TextModule.process_and_print_quotes(fquotes_dt, caption)
    # print('\n')
    # print('\n')
    return text_captions+TextModule.process_and_print_quotes(fquotes_dt1, caption)

print(text_process("fishing fishing is through a boat on the water on the boat on the water on the water on the water on the water on the water on the water on the water on the water on the water on the water on the water on the water on the water on the water on the water on the water on the water on the water on the water on the water on the water on the water on the water on"))