import io
import re
from collections import Counter
import requests
from bs4 import BeautifulSoup
import pandas as pd

class WikiScraper:
    """ Object for wiki scraping.

    Attributes: \n
        base_url: Base for the url of the wiki (e.g. https://example.com/wiki/)\n
        searched_phrase: Article name on the wiki.\n
        use_local_html_file: If true, local file is used to obtain the code. Otherwise, requests library is used to download the source code. \n
        formatted_phrase: searched_phrase, where space character is replaced with underscore.\n
        url: base_url + formatted_phrase (e.g. https://example.com/wiki/Search_Me).\n
        html: HTML code obtained with get_html() method.\n
    """

    def __init__(self, base_url, searched_phrase, use_local_html_file=False):
        """ Initializes WikiScraper object.

        :param base_url: Base for the url of the wiki (e.g. https://example.com/wiki/)
        :param searched_phrase: Article name on the wiki.
        :param use_local_html_file: If true, local file is used to obtain the code.
                                    Otherwise, requests library is used to download the source code.
        """

        if not base_url.endswith("/"):
            base_url += "/"

        self.base_url = base_url
        self.searched_phrase = searched_phrase
        self.use_local_html_file = use_local_html_file
        self.formatted_phrase = searched_phrase.replace(" ", "_")
        self.url = base_url + self.formatted_phrase
        self.html = self.get_html()

    def get_html(self):
        """ Returns HTML from self.url.

            If self.use_local_html_file is set true, HTML is obtained offline from your computer.
            Filename used is 'self.formatted_phrase.html', where formatted phrase is searched phrase
            where space character is replaced with underscore.
            Otherwise, requests library is used to download the source code.

        :return:
            In both cases, if error occurs (no file, no Internet, 404 code...)
            None is returned, with additional information printed out.
            On success, returns HTML as a string.
        """
        if self.use_local_html_file:
            file_path = self.formatted_phrase + ".html"
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
                    print(f"Oi mate, you've done something bad! "
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
        """ Returns text from the HTML.

            This method searches for div, that holds the article text,
            and then uses BeautifulSoup to extract the text.

        :return:
            If self.html is None, return None.
            If no div is found, return None with additional information printed out.
            Otherwise, return text found as a string (without HTML tags).
        """
        html = self.html
        if html is None:
            return None

        soup = BeautifulSoup(html, 'html.parser')
        element = soup.find('div', id='mw-content-text')
        if element is None:
            print("No content found.")
            return None
        text = element.get_text()
        return text

    def summary(self):
        """ Returns first paragraph of the article.

        :return:
            Returns first paragraph of the article as a string.
            If self.html is None or the paragraph is not found returns None.
        """
        html = self.html
        if html is None:
            return None

        soup = BeautifulSoup(html, 'html.parser')
        summ = soup.find('p')
        if summ is None:
            return None

        return summ.get_text()

    def find_table(self, n, first_row_is_header=False):
        """ Returns the nth table in the article.

        First column is always taken as the row indexes.

        :param n: Number of the table, starting from one.
        :param first_row_is_header: If true, first row is taken as a header.
                                    Otherwise, header is not specified.

        :return:
            On success, returns the nth table as a dataframe.
            If self.html is none, there is less than n tables in the article
            or the HTML for the table is broken (pandas couldn't read it), returns None.
        """
        html = self.html
        if html is None:
            return None

        soup = BeautifulSoup(html, 'html.parser')
        tables = soup.find_all('table', limit=n)
        if tables is None or len(tables) < n:
            return None

        if first_row_is_header:
            header_row = 0
        else:
            header_row = None

        try:
            df = pd.read_html(
                io.StringIO(str(tables[n - 1])),
                header=header_row,
                index_col=0
            )[0]
        except Exception as err:
            print(f"Unexpected error converting HTML to data frame: {err}")
            return None

        return df

    def save_table(self, df):
        """ Saves dataframe to the csv file.

            Name of the saved file is 'self.formatted_phrase.csv'.
        """

        if df is None:
            return None
        try:
            df.to_csv(self.formatted_phrase + '.csv')
        except Exception as err:
            print(f"Unexpected error: {err}")

    def count_words(self):
        """ Counts the number of each word in the article.

        :return:
            Number of each word in the article as a dictionary.
        """
        text = self.get_text()
        if text is None:
            return None
        clean_text = re.sub(r'[^a-zA-ZèéêëÈÉÊËàáâãäåÀÁÂÃÄÅ\s]', ' ', text).lower()
        words = clean_text.split()

        counted_words = Counter(words)

        return dict(counted_words)


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


