import requests
from bs4 import BeautifulSoup
from data_extractor import extract_headings, extract_paragraphs, extract_links
from config import Config
import json
import pandas as pd  # Import pandas for Excel export

class WebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': Config.USER_AGENT})

    def fetch_page(self, url):
        retries = Config.RETRIES
        for _ in range(retries):
            try:
                print(f"Fetching URL: {url}")  # Debugging statement
                response = self.session.get(url, timeout=Config.TIMEOUT)
                response.raise_for_status()
                print("Page fetched successfully!")  # Debugging statement
                return response.content
            except requests.RequestException as e:
                print(f'Error fetching {url}: {e}')
        raise Exception(f'Failed to fetch {url} after {retries} retries')

    def parse_data(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        data = {
            'headings': extract_headings(soup),
            'paragraphs': extract_paragraphs(soup),
            'links': extract_links(soup)
        }
        return data

    def display_data(self, data):
        # Sort and organize the data
        sorted_data = {
            'headings': {key: sorted(data['headings'][key]) for key in data['headings']},
            'paragraphs': sorted(data['paragraphs']),
            'links': {key: data['links'][key] for key in sorted(data['links'])}
        }

        # Display the data in an orderly manner
        print("\nHeadings:")
        for level, headings in sorted_data['headings'].items():
            print(f"  {level.upper()}:")
            for heading in headings:
                print(f"    - {heading}")

        print("\nParagraphs:")
        for paragraph in sorted_data['paragraphs']:
            print(f"  - {paragraph}")

        print("\nLinks:")
        for text, url in sorted_data['links'].items():
            print(f"  {text}: {url}")

    def export_to_excel(self, data, file_name="scraped_data.xlsx"):
        # Prepare data for Excel with classification
        headings_data = []
        for level, headings in data['headings'].items():
            for heading in headings:
                headings_data.append({'Category': 'Heading', 'Type': level.upper(), 'Content': heading})

        paragraphs_data = [{'Category': 'Paragraph', 'Type': 'Paragraph', 'Content': paragraph} for paragraph in data['paragraphs']]

        links_data = [{'Category': 'Link', 'Type': 'Link', 'Content': f"{text}: {url}"} for text, url in data['links'].items()]

        # Combine all data into a single DataFrame
        combined_data = headings_data + paragraphs_data + links_data
        df = pd.DataFrame(combined_data)

        # Export to Excel
        df.to_excel(file_name, index=False)
        print(f"Data exported to {file_name}")

    def scrape(self, url):
        html_content = self.fetch_page(url)
        data = self.parse_data(html_content)
        self.display_data(data)
        self.export_to_excel(data)  # Export data to Excel
        return data
