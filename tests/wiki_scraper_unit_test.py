import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from unittest.mock import patch, mock_open
from scraper_class import (is_relative_article_link,
                           extract_phrase,
                           add_words_to_json,
                           WikiScraper)

BASE_URL = "https://bulbapedia.bulbagarden.net/wiki/"

@pytest.mark.parametrize("link, expected", [
    (BASE_URL, False),
    ('/wiki/', False),
    ('', False),
    (None, False),
    (0, False),
    (1, False),
    ('wiki/Team_Rocket', False),
    ('/wiki/a:bc', False),
    ('/wiki/abc', True),
    ('/wiki/a', True),
    ('/wiki/Team_Rocket', True),
    ('/wiki/still/valid', True)
])
def test_is_article_link(link, expected):
    assert is_relative_article_link(link) is expected

@pytest.mark.parametrize("link, expected", [
    (BASE_URL, None),
    ('/wiki/', None),
    ('', None),
    (None, None),
    (0, None),
    (1, None),
    ('wiki/Team_Rocket', None),
    ('/wiki/a:bc', None),
    ('/wiki/abc', 'abc'),
    ('/wiki/a', 'a'),
    ('/wiki/Team_Rocket', 'Team_Rocket'),
])
def test_extract_phrase(link, expected):
    assert extract_phrase(link) == expected

def test_add_words_to_json(tmp_path):
    file = tmp_path / 'word-counts.json'

    to_add1 = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6}
    expected1 = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6}
    add_words_to_json(to_add1, file)

    assert file.exists()
    with open(file, 'r') as f:
        assert json.load(f) == expected1

    add_words_to_json(to_add1, file)

    expected2 = {'A': 2, 'B': 4, 'C': 6, 'D': 8, 'E': 10, 'F': 12}

    assert file.exists()
    with open(file, 'r') as f:
        assert json.load(f) == expected2

    to_add2 = {'A': 1, 'g': 111}
    add_words_to_json(to_add2, file)

    expected3 = {'A': 3, 'B': 4, 'C': 6, 'D': 8, 'E': 10, 'F': 12, 'g': 111}
    with open(file, 'r') as f:
        assert json.load(f) == expected3

def test_check_html():

    scraper = WikiScraper("base_url", "fake_article", use_local_html_file=True)
    assert scraper.check_html() is False

    fake_html = "<html><body><<h1>THIS IS REAL SITE!! GIMME MONEY@!!@</h1><p>WHEE WHOO</p></body></html>"
    fake_html_with_div = "<html><body><div id='content'><h1>THIS IS REAL SITE!! GIMME MONEY@!!@</h1><p>WHEE WHOO</p></div></body></html>"

    #Test for HTML without div of a content.
    with patch("builtins.open", mock_open(read_data=fake_html)) as mock_file:
        scraper2 = WikiScraper("base_url", "fake_site", use_local_html_file=True)
        assert scraper2.check_html() is False
        mock_file.assert_called_once_with('fake_site.html', 'r')

    # with div
    with patch("builtins.open", mock_open(read_data=fake_html_with_div)) as mock_file:
        scraper3 = WikiScraper("base_url", "fake_site", use_local_html_file=True)
        assert scraper3.check_html() is True
        mock_file.assert_called_once_with('fake_site.html', 'r')

if __name__ == "__main__":
    exit(pytest.main())