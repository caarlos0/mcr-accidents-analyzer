import requests
from bs4 import BeautifulSoup
import csv
import re


def is_relevant_article(title, description):
    keywords = ["marechal candido rondon", "marechal rondon"]
    content = (title + " " + description).lower()

    # Check if the content contains any of the keywords
    keyword_match = any(keyword in content for keyword in keywords)

    # Check if the content does NOT match the regex pattern
    road_pattern = re.compile(r'[BP]R[ -]\d+', re.IGNORECASE)
    no_road_match = not road_pattern.search(content)

    # Article is relevant if it contains a keyword and doesn't match the road pattern
    return keyword_match and no_road_match

def scrape_and_write(url, writer):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 404:
        return False, 0
    elif response.status_code != 200:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return False, 0

    soup = BeautifulSoup(response.content, 'html.parser')
    articles = soup.find_all('a', class_=['lista-interna', 'img-lista-s'])

    articles_written = 0
    for article in articles:
        href = article.get('href')
        title_div = article.find('div', class_='titulo-sub-lista')

        if title_div:
            spans = title_div.find_all('span')
            if len(spans) >= 2:
                title = spans[0].text.strip()
                description = spans[1].text.strip()

                if is_relevant_article(title, description):
                    writer.writerow([title, description, href])
                    articles_written += 1

    return True, articles_written

def scrape_marechalnews():
    base_url = 'https://marechalnews.com.br/transito/pagina/'
    page_number = 1
    total_articles = 0

    with open('marechal_rondon_articles.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Title', 'Description', 'URL'])  # Header

        while True:
            url = f"{base_url}{page_number}"
            print(f"Scraping page {page_number}...")

            success, articles_written = scrape_and_write(url, writer)
            if not success:
                print(f"Reached end of pages at page {page_number - 1}")
                break

            total_articles += articles_written
            print(f"Found {articles_written} relevant articles on this page")
            page_number += 1

    print(f"Scraped a total of {total_articles} relevant articles and saved to marechal_rondon_articles.csv")

if __name__ == "__main__":
    scrape_marechalnews()
