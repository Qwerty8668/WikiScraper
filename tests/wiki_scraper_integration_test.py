import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from wiki_scraper import WikiScraper

def test_summary():
    """Test the summary function."""
    scraper = WikiScraper(base_url='https://bulbapedia.bulbagarden.net/wiki/',
                searched_phrase="Team Rocket",
                use_local_html_file=True)

    assert scraper.check_html() == True

    summary = scraper.summary()

    expected = ("Team Rocket (Japanese: ロケット団 Rocket-dan, literally Rocket Gang) "
                "is a villainous team in pursuit of evil and the exploitation of Pokémon. "
                "The organization is based in the Kanto and Johto regions, with a small "
                "outpost in the Sevii Islands.\n")

    assert summary == expected

if __name__ == "__main__":
    import pytest
    exit(pytest.main())