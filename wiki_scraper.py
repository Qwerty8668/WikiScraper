import argparse
from scraper import (WikiScraper,
                     add_words_to_json,
                     analyze_relative_word_frequency,
                     auto_count_words)

def parse_arguments():
    """Parse command line arguments using argparse.

    :return:
        parser.parse_args()
    """
    parser = argparse.ArgumentParser(
        prog='wiki_scraper',
        description='Scraper for bulbapedia wiki',
    )

    group = parser.add_argument_group('Summary')
    group.add_argument('--summary', type=str,
                       help='Summary of the given wiki article.')

    group = parser.add_argument_group('Table')
    group.add_argument('--table', type=str,
                       help='Show table from the given wiki article and count values in it.')
    group.add_argument('--number', type=int,
                       help='Number of the table, starting from one.')
    group.add_argument('--first-row-is-header', action='store_true', default=False,
                       help='If true, first row is taken as a header. Otherwise, header is not specified.')

    group = parser.add_argument_group('Word counting')
    group.add_argument('--count-words', type=str,
                       help='Count words in the given wiki article. Updates word-counts.json file.')

    group = parser.add_argument_group('Word frequency analysis')
    group.add_argument('--analyze-relative-word-frequency', action='store_true', default=False,
                       help='Compares the frequencies of words counted in JSON file to the frequencies '
                            'of the top english words.')
    group.add_argument('--mode', type=str, choices=['language', 'article'],
                       help="'language' or 'article' - to decide which top words to take.")
    group.add_argument('--count', type=int,
                       help="How many words to compare.")
    group.add_argument('--chart', type=str,
                       help="Optional: path, where to save the chart.")

    group = parser.add_argument_group('Auto word counting')
    group.add_argument('--auto-count-words', type=str,
                       help="Automatically counts words in the articles, iterating through them using onsite links.")
    group.add_argument('--depth', type=int,
                       help="Number of links to check.")
    group.add_argument('--wait', type=float,
                       help="Time to wait between site downloads.")

    return parser.parse_args()


class WikiController:
    """Object, that parses arguments from user and uses proper functions in WikiScraper."""

    def __init__(self, base_url, args):
        """Initialize the WikiController object.

        :param base_url: Base for the url of the wiki (e.g. https://example.com/wiki/).
        :param args: Arguments parsed from user.
        """
        self.base_url = base_url
        self.args = args
        
    def validate_arguments(self):
        """Validate the arguments from the user."""

        def is_not_none(arg):
            if arg is None:
                return False
            return True

        # --table and --number not together.
        if is_not_none(self.args.table) != is_not_none(self.args.number):
            raise ValueError("--table and --number should be used together.")

        # --first-row-is-header without --table.
        if self.args.first_row_is_header and self.args.table is None:
            raise ValueError("--first-row-is-header is an optional argument for --table.")

        # --analyze-relative-word-frequency, --mode and --count not together
        requirements = (bool(self.args.analyze_relative_word_frequency) + is_not_none(self.args.mode)
                        + is_not_none(self.args.count))
        if requirements not in [0, 3]:
            raise ValueError("--analyze-relative-word-frequency, --mode and --count should be used together.")

        # --chart without --analyze-relative-word-frequency
        if self.args.chart and not self.args.analyze_relative_word_frequency:
            raise ValueError("--chart is an optional argument for --analyze-relative-word-frequency.")

        # --auto-count-words, --depth and --wait not together
        requirements = (is_not_none(self.args.auto_count_words) + is_not_none(self.args.depth)
                        + is_not_none(self.args.wait))
        if requirements not in [0, 3]:
            raise ValueError("--auto_count_words, --depth and --wait should be used together.")

        # --number less than one
        if self.args.number is not None and self.args.number < 1:
            raise ValueError("--number should be a positive integer.")

        # --count less than one
        if self.args.count is not None and self.args.count < 1:
            raise ValueError("--count should be a positive integer.")

        # --depth less than one
        if self.args.depth is not None and self.args.depth < 1:
            raise ValueError("--depth should be a positive integer.")

        # -- wait less than zero
        if self.args.wait is not None and self.args.wait < 0:
            raise ValueError("--wait should be greater than 0.")
    
    def run(self):
        """Validate arguments and use WikiScraper to scrape data."""

        try:
            self.validate_arguments()
        except ValueError as e:
            print("Argument error:", e)
            exit(1)

        # --summary "searched phrase"
        if self.args.summary is not None:
            print("=== SUMMARY ===")
            scraper = WikiScraper(self.base_url, self.args.summary)
            if scraper.check_html():
                summary = scraper.summary()
                if summary is not None:
                    print(summary)
                scraper.print_license_footer()
            print()

        # --table "searched phrase" --number n [--first-row-is-header]
        if self.args.table is not None:
            print("=== TABLE ===")
            scraper = WikiScraper(self.base_url, self.args.table)
            if scraper.check_html():
                table, count = scraper.find_table(self.args.number, self.args.first_row_is_header)
                if table is not None:
                    print(table)
                    scraper.save_table(table)

                if count is not None:
                    print(count)
                scraper.print_license_footer()
            print()

        # --count-words "searched phrase"
        if self.args.count_words is not None:
            print('=== COUNT WORDS ===')
            scraper = WikiScraper(self.base_url, self.args.count_words)
            if scraper.check_html():
                count = scraper.count_words()
                add_words_to_json(count)
                print("JSON updated.")
                scraper.print_license_footer()
            print()


        # --analyze-relative-word-frequency --mode "language|article"
        # --count n [--chart "path/to/save/chart.png"]
        if self.args.analyze_relative_word_frequency:
            print("=== ANALYSIS ===")
            if self.args.chart is not None:
                chart = True
            else:
                chart = False
            df = analyze_relative_word_frequency(self.args.mode, self.args.count, chart, self.args.chart)
            if df is not None:
                print(df)
            print()

        # --auto-count-words "searched phrase" --depth n --wait t
        if self.args.auto_count_words is not None:
            print("=== AUTO COUNT WORDS ===")
            auto_count_words(self.base_url, self.args.auto_count_words, self.args.depth, self.args.wait)
            print("-" * 40)
            print(f"Program output based on the article available at: {self.base_url}")
            print("Content is subject to the wiki's license BY-NC-SA.")
            print("Please verify the license before further use.")
            print("-" * 40)
            print()

# Main function.
if __name__ == "__main__":

    args = parse_arguments()

    controller = WikiController('https://bulbapedia.bulbagarden.net/wiki/', args)

    controller.run()