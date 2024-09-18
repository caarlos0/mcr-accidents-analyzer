import requests
from bs4 import BeautifulSoup
import csv
import re

def is_relevant_article(title, description, url):
    keywords = ["marechal candido rondon", "marechal rondon", "marechal-candido-rondon"]
    content = (title + " " + description + " " + url).lower()

    keyword_match = any(keyword in content for keyword in keywords)
    road_pattern = re.compile(r'[BP]R[ -]\d+', re.IGNORECASE)
    no_road_match = not road_pattern.search(content)

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
    articles = soup.find_all('li', class_='mvp-blog-story-wrap')

    articles_written = 0
    for article in articles:
        link_element = article.find('a')
        story_in_div = article.find('div', class_='mvp-blog-story-in')

        if link_element and story_in_div:
            href = link_element['href']
            title_element = story_in_div.find('h2')
            description_element = story_in_div.find('p')

            if title_element and description_element:
                title = title_element.text.strip()
                description = description_element.text.strip()

                if is_relevant_article(title, description, href):
                    writer.writerow([title, description, href])
                    articles_written += 1

    return True, articles_written

def scrape_opresente():
    base_url = 'https://www.opresente.com.br/page/{}/?s=acidente'
    page_number = 66
    total_articles = 0

    with open('opresente_accident_articles.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Title', 'Description', 'URL'])  # Header

        while True:
            url = base_url.format(page_number)
            print(f"Scraping page {page_number}...")

            success, articles_written = scrape_and_write(url, writer)
            if not success:
                print(f"Reached end of pages at page {page_number - 1}")
                break

            total_articles += articles_written
            print(f"Found {articles_written} relevant articles on this page")
            page_number += 1

    print(f"Scraped a total of {total_articles} relevant articles and saved to opresente_accident_articles.csv")

if __name__ == "__main__":
    scrape_opresente()
