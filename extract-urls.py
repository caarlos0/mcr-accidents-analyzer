import requests
from bs4 import BeautifulSoup
import time

def scrape_page(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_urls(html):
    soup = BeautifulSoup(html, 'html.parser')
    li_elements = soup.select('li.mvp-blog-story-wrap')
    for li in li_elements:
        a_tag = li.find('a')
        if a_tag and 'href' in a_tag.attrs:
            print(a_tag['href'])
            with open('urls.txt', 'a') as f:
                f.write(f"{a_tag['href']}\n")

def main():
    base_url = 'https://www.opresente.com.br/page/{}/?s=acidente'
    page_number = 1
    all_urls = set()

    while True:
        url = base_url.format(page_number)
        print(f"Scraping page {page_number}: {url}")

        html = scrape_page(url)
        if html is None:
            print(f"Reached the end at page {page_number - 1}")
            break

        extract_urls(html)

        page_number += 1

    print("URLs have been saved to urls.txt")

if __name__ == "__main__":
    main()
