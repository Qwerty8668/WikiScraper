import io
import re
from collections import Counter
import requests
from bs4 import BeautifulSoup
import pandas as pd

class WikiScraper:
    def __init__(self, base_url, searched_phrase, use_local_html_file=False):

        if not base_url.endswith("/"):
            base_url += "/"

        self.base_url = base_url
        self.searched_phrase = searched_phrase
        self.use_local_html_file = use_local_html_file
        self.formatted_phrase = searched_phrase.replace(" ", "_")
        self.url = base_url + self.formatted_phrase
        self.html = self.get_html()

    def get_html(self):
        if self.use_local_html_file:
            file_path = self.formatted_phrase.lower() + ".html"
            try:
                with open(file_path, "r") as file:
                    html = file.read()
                    return html

            except FileNotFoundError:
                print("File not found!")

            except Exception as err:
                print(f"Unexpected error: {err}")

            return None

        else:
            try:
                response = requests.get(self.url)
                response.raise_for_status()

                return response.text

            except requests.exceptions.HTTPError as err:
                status_code = err.response.status_code

                if status_code == 404:
                    print(f"Site {self.url} not found (error code 404).")
                    print("Wiki is case-sensitive. Check for spelling "
                          "mistakes or if the site still exists.")

                elif status_code == 403:
                    print(f"Site {self.url} is forbidden for the mortals "
                          f"(error code 403).")

                elif 400 <= status_code < 500:
                    print(f"Site {self.url} could not be accessed.")
                    print(f"Oi mate, you've done somethin' bad! "
                          f"(error code {status_code}).")

                elif status_code >= 500:
                    print(f"Site {self.url} cannot be reached (not your fault tho!)"
                          f" (error code {status_code}).")

            except requests.exceptions.ConnectionError as e:
                print(f"Connection Error: Check your internet connection.")

            except requests.exceptions.Timeout as e:
                print(f"Timeout Error: Server is not responding.")

            except Exception as err:
                print(f"Unexpected error: {err}")

            return None

    def get_text(self):
        html = self.html
        if html is None:
            return None

        soup = BeautifulSoup(html, 'html.parser')
        element = soup.find('div', id='mw-content-text')
        text = element.get_text()
        return text

    def summary(self):
        html = self.html
        if html is None:
            return None
        soup = BeautifulSoup(html, 'html.parser')
        summ = soup.find('p')
        if summ is None:
            return "No paragraph to display."
        return summ.get_text()

    def find_table(self, n, first_row_is_header=False):
        html = self.html
        if html is None:
            return None

        soup = BeautifulSoup(html, 'html.parser')
        tables = soup.find_all('table')
        if tables is None:
            return None

        if first_row_is_header:
            header_row = 0
        else:
            header_row = None
        df = pd.read_html(
            io.StringIO(str(tables[n - 1])),
            header=header_row,
            index_col=0
        )[0]

        return df

    def save_table(self, df):
        if df is None:
            return None
        try:
            df.to_csv(self.formatted_phrase + '.csv', index = False)
        except Exception as err:
            print(f"Unexpected error: {err}")

    def count_words(self):
        text = self.get_text()
        if text is None:
            return None
        clean_text = re.sub(r'[^a-zA-ZèéêëÈÉÊËàáâãäåÀÁÂÃÄÅ\s]', ' ', text).lower()
        words = clean_text.split()

        counted_words = Counter(words)

        return counted_words


scraper = WikiScraper(
    base_url="https://bulbapedia.bulbagarden.net/wiki/",
    searched_phrase = input("Search: ")
)
print(scraper.get_text())

table = scraper.find_table(2, first_row_is_header=False)
print(table)

d = scraper.count_words()
print(d)

scraper.save_table(table)


