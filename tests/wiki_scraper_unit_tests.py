from unittest.mock import patch, mock_open
from scraper_class import (is_relative_article_link,
                           extract_phrase,
                           add_words_to_json,
                           WikiScraper)

BASE_URL = "https://bulbapedia.bulbagarden.net/wiki/"

def test_is_article_link():
    assert is_relative_article_link(BASE_URL) is False
    assert is_relative_article_link('/wiki/') is False
    assert is_relative_article_link('') is False
    assert is_relative_article_link(None) is False
    assert is_relative_article_link(0) is False
    assert is_relative_article_link(1) is False
    assert is_relative_article_link('wiki/Team_Rocket') is False
    assert is_relative_article_link('/wiki/a:bc') is False

    assert is_relative_article_link('/wiki/abc') is True
    assert is_relative_article_link('/wiki/abc1') is True
    assert is_relative_article_link('/wiki/a') is True
    assert is_relative_article_link('/wiki/Team_Rocket') is True
    assert is_relative_article_link('/wiki/still/valid') is True

def test_extract_phrase():
    assert extract_phrase(BASE_URL) is None
    assert extract_phrase('/wiki/') is None
    assert extract_phrase('') is None
    assert extract_phrase(None) is None
    assert extract_phrase(0) is None
    assert extract_phrase(1) is None
    assert extract_phrase('wiki/Team_Rocket') is None
    assert extract_phrase('/wiki/a:bc') is None

    assert extract_phrase('/wiki/abc') == 'abc'
    assert extract_phrase('/wiki/abc1') == 'abc1'
    assert extract_phrase('/wiki/a') == 'a'
    assert extract_phrase('/wiki/Team_Rocket') == 'Team_Rocket'
    assert extract_phrase('/wiki/still/valid') == 'still/valid'

def test_add_words_to_json(tmp_path):
    file = tmp_path / 'word-counts.json'

    to_add1 = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6}

    expected1 = ('{\n''    "A": 1,\n''    "B": 2,\n''    "C": 3,\n''    "D": 4,\n''    "E": 5,\n''    "F": 6\n''}')

    add_words_to_json(to_add1, file)

    assert file.exists()
    assert file.read_text() == expected1

    add_words_to_json(to_add1, file)

    expected2 = ('{\n''    "A": 2,\n''    "B": 4,\n''    "C": 6,\n''    "D": 8,\n''    "E": 10,\n''    "F": 12\n''}')

    assert file.exists()
    assert file.read_text() == expected2

    to_add2 = {'A': 1, 'g': 111}
    add_words_to_json(to_add2, file)

    expected3 = ('{\n''    "A": 3,\n''    "B": 4,\n''    "C": 6,\n''    "D": 8,\n''    "E": 10,\n''    "F": 12,\n''    "g": 111\n''}')

    assert file.exists()
    assert file.read_text() == expected3

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
