import io
import json
import math
import os
import time
from collections import Counter
import numpy as np
import requests
from bs4 import BeautifulSoup
import pandas as pd
import wordfreq as wf
import matplotlib.pyplot as plt

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
        """ Returns HTML of the article (without menu of the site) from self.url.

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

                soup = BeautifulSoup(response.text, 'html.parser')
                element = soup.find('div', id='content')
                if element is None:
                    print("No content found.")
                    return None

                return str(element)

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

            except requests.exceptions.ConnectionError:
                print(f"Connection Error: Check your internet connection.")

            except requests.exceptions.Timeout:
                print(f"Timeout Error: Server is not responding.")

            except Exception as err:
                print(f"Unexpected error: {err}")

            return None

    def get_text(self):
        """ Returns text from the HTML.

            Uses BeautifulSoup to extract the text from the article.

        :return:
            If self.html is None, return None.
            If no div is found, return None with additional information printed out.
            Otherwise, return text found as a string (without HTML tags).
        """
        html = self.html
        if html is None:
            return None

        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
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
        """ Returns the nth table in the article and table of number of each word in the table.

        First column is always taken as the row indexes.

        :param n: Number of the table, starting from one.
        :param first_row_is_header: If true, first row is taken as a header.
                                    Otherwise, header is not specified.

        :return:
            On success, returns the nth table as a dataframe and dataframe with counted words.
            If self.html is none, there is less than n tables in the article
            or the HTML for the table is broken (pandas couldn't read it), returns None.
        """
        html = self.html
        if html is None:
            return None

        soup = BeautifulSoup(html, 'html.parser')
        tables = soup.find_all('table', limit=n)
        if tables is None or len(tables) < n:
            print(f"There is less than {n} table in the article.")
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

        count = (pd.Series(df.values.flatten()) # flatten the df into one column, without labels.
                 .value_counts()
                 .reset_index()
                 .set_axis(['words', 'count'], axis=1)
                 )

        return df, count

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

        words = wf.tokenize(text, lang='en')

        counted_words = Counter(words)

        return dict(counted_words)

    def get_article_links(self):
        """ Returns a list of links from the website, that directs to another wiki article.

        :return:
            Python list of links on the website that starts with self.base_url
        """
        html = self.html
        if html is None:
            return None

        soup = BeautifulSoup(html, 'html.parser')

        all_links = soup.find_all('a')
        wiki_article_links = []
        for link in all_links:
            if link.has_attr('href'):
                link = link['href']
                # We are taking only links that stay in the wiki, and we are skipping things like 'File:' 'User:' etc.
                if link.startswith('/wiki/') and not ':' in link:
                    wiki_article_links.append(link)

        return wiki_article_links

'''============================ OTHER METHODS =============================='''

def add_words_to_json(words, filename="words_count.json"):
    """ Adds counted words to the JSON file.

    :param words: Dictionary of words, with their count as a value.
    :param filename: Name of the file to add the words count.
    """

    if os.path.isfile(filename):
        with open(filename, 'r') as f:
            try:
                old_data = json.load(f)
            except json.JSONDecodeError:
                old_data = {}
    else:
        old_data = {}

    new_data = Counter(old_data) + Counter(words)

    with open(filename, 'w') as f:
        json.dump(new_data, f, indent=4)

def auto_count_words(base_url, searched_phrase, n, t, visited=None):
    """Automatically counts words in the articles, iterating through them using onsite links.

    Recursively performs DFS on found links. Goes through maximally n links, waits t seconds before going to the next link.

    :param base_url: Base for the url of the wiki (e.g. https://example.com/wiki/)
    :param searched_phrase: Phrase to search for.
    :param n: Number of links yet to check.
    :param t: Time between site downloads.
    :param visited: Dictionary of visited links.
    """
    if visited is None:
        visited = {}
    if visited.get(searched_phrase, False):
        return n

    visited[searched_phrase] = True
    print(n, searched_phrase)
    n -= 1
    scraper = WikiScraper(base_url, searched_phrase, False)
    count = scraper.count_words()
    add_words_to_json(count)

    links = scraper.get_article_links()

    for link in links:
        if n == 0: return 0
        phrase = link[6:] # Delete '/wiki/' prefix.
        time.sleep(t)
        n = auto_count_words(base_url, phrase, n, t, visited)

    return n

def analyze_relative_word_frequency(mode, n, chart=False, chart_path=None, filename="words_count.json"):
    """ Performs analysis of the words counted in the JSON file.

        Compares the frequencies of words counted in JSON file to the frequencies
        of the top english words. Depending on 'mode' parameter it takes top
        n words in english language or top n words from counted words.

        :param mode: 'language' or 'article' - to decide which top words to take.
        :param n: How many words to compare.
        :param filename: Name of the JSON file with counted words. Defaults to 'words_count.json'.
        :param chart: If true, creates grouped bar chart comparing frequencies of the words.
        :param chart_path: path, where to save the chart. If None, current directory is used.

    :return:
        Returns DataFrame with three columns: word, frequency in the article, frequency in english.
        If frequency of the word is zero, DataFrame contains NaN there.
        If specified directory for the chart cannot be created or accessed, still returns DataFrame.

    """
    if os.path.isfile(filename):
        with open(filename, 'r') as f:
            try:
                my_data = json.load(f)
            except json.JSONDecodeError:
                my_data = {}
    else:
        my_data = {}

    words_total = sum(my_data.values())

    df = pd.DataFrame([], columns=['word', 'frequency in the article', 'frequency in english'])

    if mode == 'language':
        top_n_words = wf.top_n_list(lang='en', n=n, wordlist='small')
    elif mode == 'article':
        top_n_words = dict(sorted(my_data.items(), key=lambda item: item[1], reverse=True)[:n])
    else:
        print(f"No mode named {mode}")
        return None

    for word in top_n_words:
        my_freq = my_data.get(word, 0) / words_total
        if my_freq > 0:
            my_zipf = math.log10(my_freq * 10 ** 9)
        else:
            my_zipf = np.nan

        # Wordfreq zipf values are also rounded like that.
        my_zipf = round(my_zipf, 2)

        lang_zipf = wf.zipf_frequency(word, lang='en', wordlist='small')

        if lang_zipf == 0:
            lang_zipf = np.nan

        new_row = pd.DataFrame([[word, my_zipf, lang_zipf]],
                               columns=['word', 'frequency in the article', 'frequency in english'])
        df = pd.concat([df, new_row], ignore_index=True)

    if chart:
        if chart_path is None:
            chart_path = 'chart.png'

        dirname = os.path.dirname(chart_path)

        if dirname and not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except OSError:
                print(f'Error: Creating directory {dirname}')
                return df

        df.plot(
            x='word',
            y=['frequency in the article', 'frequency in english'],
            kind='bar',
            color=['blue', 'red'],
            rot=0,
            width=0.6
        )

        plt.title("Frequency of some words on Wiki")
        plt.ylabel("frequency")
        plt.xlabel("")
        plt.legend(["Wiki", "English"])
        try:
            plt.savefig(chart_path)
        except OSError:
            print("Error: Saving the chart is not possible.")
            return df
    return df