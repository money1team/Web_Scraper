import argparse
import json
import sys
from scraper import WebScraper
from config import Config

def main():
    parser = argparse.ArgumentParser(description='Web Scraper')
    parser.add_argument('url', type=str, help='URL of the website to scrape')
    parser.add_argument('--output', type=str, default='output.json', help='Output file name')
    args = parser.parse_args()

    scraper = WebScraper()
    try:
        data = scraper.scrape(args.url)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f'Scraped data saved to {args.output}')
    except Exception as e:
        print(f'An error occurred: {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()
