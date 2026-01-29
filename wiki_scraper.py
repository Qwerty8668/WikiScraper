import argparse
from scraper_class import (WikiScraper,
                           add_words_to_json,
                           analyze_relative_word_frequency,
                           auto_count_words)

def parse_arguments():
    parser = argparse.ArgumentParser(
        prog='wiki_scraper',
        description='Scraper for bulbapedia wiki',
    )

    parser.add_argument('--summary', type=str)

    parser.add_argument('--table', type=str)
    parser.add_argument('--number', type=int)
    parser.add_argument('--first-row-is-header', action='store_true', default=False)

    parser.add_argument('--count-words', type=str)

    parser.add_argument('--analyze-relative-word-frequency', action='store_true', default=False)
    parser.add_argument('--mode', type=str, choices=['language', 'article'])
    parser.add_argument('--count', type=int)
    parser.add_argument('--chart', type=str)

    parser.add_argument('--auto-count-words', type=str)
    parser.add_argument('--depth', type=int)
    parser.add_argument('--wait', type=int)

    return parser.parse_args()


class WikiController:

    def __init__(self, base_url, args):
        self.base_url = base_url
        self.args = args
        
    def validate_arguments(self):

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
        requirements = bool(self.args.analyze_relative_word_frequency) + is_not_none(self.args.mode) + is_not_none(self.args.count)
        if requirements not in [0, 3]:
            raise ValueError("--analyze-relative-word-frequency, --mode and --count should be used together.")

        # --chart without --analyze-relative-word-frequency
        if self.args.chart and not self.args.analyze_relative_word_frequency:
            raise ValueError("--chart is an optional argument for --analyze-relative-word-frequency.")

        # --auto-count-words, --depth and --wait not together
        requirements = is_not_none(self.args.auto_count_words) + is_not_none(self.args.depth) + is_not_none(self.args.wait)
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

        try:
            self.validate_arguments()
        except ValueError as e:
            print("Argument error:", e)
            exit(1)

        # --summary "searched phrase"
        if self.args.summary is not None:
            scraper = WikiScraper(self.base_url, self.args.summary)
            summary = scraper.summary()
            if summary is not None:
                print(summary)

        # --table "searched phrase" --number n [--first-row-is-header]
        if self.args.table is not None:
            scraper = WikiScraper(self.base_url, self.args.table)
            table, count = scraper.find_table(self.args.number, self.args.first_row_is_header)
            if table is not None:
                print(table)
                scraper.save_table(table)

            if count is not None:
                print(count)

        # --count-words "searched phrase"
        if self.args.count_words is not None:
            scraper = WikiScraper(self.base_url, self.args.count_words)
            count = scraper.count_words()
            add_words_to_json(count)

        # --analyze-relative-word-frequency --mode "language|article"
        # --count n [--chart "path/to/save/chart.png"]
        if self.args.analyze_relative_word_frequency:
            if self.args.chart is not None:
                chart = True
            else:
                chart = False
            df = analyze_relative_word_frequency(self.args.mode, self.args.count, chart, self.args.chart)
            if df is not None:
                print(df)

        # --auto-count-words "searched phrase" --depth n --wait t
        if self.args.auto_count_words is not None:
            auto_count_words(self.base_url, self.args.auto_count_words, self.args.depth, self.args.wait)


if __name__ == "__main__":

    args = parse_arguments()

    controller = WikiController('https://bulbapedia.bulbagarden.net/wiki/', args)

    controller.run()