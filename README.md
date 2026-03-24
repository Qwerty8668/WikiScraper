# WikiScraper

WikiScraper is a modular Python command-line tool designed to download, parse, and analyze data from Bulbapedia. It offers a suite of features including text extraction, tabular data parsing, word frequency counting, and automated web crawling. Additionally, the project features a Jupyter Notebook for analyzing language confidence scores based on word frequencies.

## Features

* **Summary Extraction:** Fetches the first paragraph of an article for a given phrase, stripping away all HTML tags.
* **Table Extraction:** Locates the *n*-th table on a page, extracts its text data, and saves it directly to a CSV file (compatible with Pandas).
* **Word Counting:** Analyzes the article's text, counts word occurrences, and updates a serialized JSON dictionary (`word-counts.json`).
* **Relative Frequency Analysis:** Compares the frequency of words found on the wiki to standard English language frequencies, normalizing the data and generating comparative bar charts.
* **Automated Web Crawling:** Follows internal wiki links up to a specified depth to perform bulk word counting, featuring built-in wait times to respect server limits.
* **Language Confidence Analysis:** Includes a Jupyter Notebook (`lang_confidence_score.ipynb`) that implements and evaluates a custom language detection function against multiple languages.

## Project Structure

```text
.
└── WikiScraper
    ├── lang_confidence/
    │   ├── data/
    │   │   ├── english_article.html
    │   │   ├── polish_article.html
    │   │   └── spanish_article.html
    │   ├── __init__.py
    │   └── lang_confidence_score.ipynb
    ├── tests/
    │   ├── fixtures/
    │   │   └── Team_Rocket.html
    │   ├── __init__.py
    │   ├── wiki_scraper_integration_test.py
    │   └── wiki_scraper_unit_test.py
    ├── scraper.py
    └── wiki_scraper.py
```
## Installation

1. Clone the repository.
2. Create and activate a virtual environment:
   * **Linux/macOS:** `python -m venv venv && source venv/bin/activate`
   * **Windows:** `python -m venv venv` and then `venv\Scripts\activate`
3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
## Usage

Run the program via the command line. The argument format generally expects a search phrase enclosed in quotes.
### Get an article summary:
    
    python wiki_scraper.py --summary "Team Rocket"

### Extract the 2nd table from an article and save to CSV:
    
    python wiki_scraper.py --table "Type" --number 2 --first-row-is-header
### Count words in an article:
    
    python wiki_scraper.py --count-words "Pikachu"

### Analyze word frequency and generate a chart:
    
    python wiki_scraper.py --analyze-relative-word-frequency --mode article --count 10 --chart "output_chart.png"
    
### Auto-crawl and count words starting from a phrase (depth of 2, waiting 1 second between requests):
    
    python wiki_scraper.py --auto-count-words "Bulbasaur" --depth 2 --wait 1

## Testing

The project includes both unit tests and integration tests that mock internet connections using local HTML fixtures.

Run the test suite using pytest:

    pytest tests/


## License

The output of this program is based on articles available on Bulbapedia, which is licensed under the CC BY-NC-SA license.
