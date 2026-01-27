import requests
import os
from bs4 import BeautifulSoup

# Tworzymy jedną instancje klasy dla jednej STRONY wiki.
class WikiScraper:
    def __init__(self, base_url, searched_phrase, use_local_html_file=False):

        if not base_url.endswith("/"):
            base_url += "/"

        self.base_url = base_url
        self.searched_phrase = searched_phrase
        self.use_local_html_file = use_local_html_file
        self.formatted_phrase = searched_phrase.replace(" ", "_")
        self.url = base_url + self.formatted_phrase

    def get_html(self):
        if self.use_local_html_file:
            file_path = self.formatted_phrase.lower() + ".html"
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Nie znaleziono pliku lokalnego: {file_path}")
        else:
            response = requests.get(self.url)
            if response.ok:
                html = response.text
                return html
            elif response.status_code == 404:
                print("Site " + self.url + " not found (error code 404). "
                      "Wiki is case-sensitive. Check for spelling mistakes "
                      "or if the site still exists.")
            elif response.status_code == 403:
                print("Site " + self.url + " is forbidden for the mortals "
                      "(error code 403).")
            elif 400 <= response.status_code < 500:
                print("Site " + self.url + " could not be accesed.\nOi mate, "
                      "you've done something bad (error code "
                      + str(response.status_code) + ").")
            elif response.status_code >= 500:
                print("Site " + self.url + "cannot be reached (not your fault tho!)"
                      " (error code " + str(response.status_code) + ").")
            return None

    def get_text(self):
        html = self.get_html()
        if html is None:
            return None

        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        return text

    def summary(self):
        html = self.get_html()
        if html is None:
            return None
        soup = BeautifulSoup(html, 'html.parser')
        summ = soup.find('p')
        if summ is None:
            return "No paragraph to display."
        return summ.text


scraper = WikiScraper(
    base_url="https://bulbapedia.bulbagarden.net/wiki/",
    searched_phrase = input("Search: ")
)
print(scraper.summary())

