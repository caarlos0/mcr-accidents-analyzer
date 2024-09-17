import requests
from bs4 import BeautifulSoup
import json
import time
import os
import sqlite3
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def create_database():
    conn = sqlite3.connect('articles.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        address TEXT,
        title TEXT,
        url TEXT UNIQUE,
        is_roundabout BOOLEAN,
        fatal_victims INTEGER
    )
    ''')
    conn.commit()
    conn.close()

def fetch_article_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        article = soup.find('article')
        if article:
            # Remove all HTML tags and get the text content
            return ' '.join(article.stripped_strings)
        return None
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def process_with_claude(article_content, url):
    prompt = f"{HUMAN_PROMPT}Extract information from the following article and format it as JSON. The JSON should include the following fields: date (in yyyy-MM-dd format), address, title, url, is_roundabout (boolean), and fatal_victims (integer). If a piece of information is not present, use null for the value. Here's the article:\n\n{article_content}\n\nThe URL for this article is: {url}\n\nIf the article is not about a traffic accident involving cars and/or motorcycles, return an empty JSON object.\nAccidents that occur in roudabouts usually contains the words 'rotatoria', 'rotula', or 'posto da mirta'. Exclude news about plane crashes and any news outside of marechal candido rondon. Only return the JSON if the accident was inside the city of marechal candido rondon\n{AI_PROMPT}"

    try:
        result = client.messages.create(
            max_tokens=int((len(prompt) // 4) * 1.5),
            system="You are a news categorization engine that outputs JSON files. You return ONLY the JSON, nothing else.",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="claude-3-sonnet-20240229",
        )
        return result.content[0].text
    except Exception as e:
        print(f"Error processing with Claude: {e}")
        return None

def insert_into_database(data):
    conn = sqlite3.connect('articles.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
        INSERT OR IGNORE INTO articles (date, address, title, url, is_roundabout, fatal_victims)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data.get('date'),
            data.get('address'),
            data.get('title'),
            data.get('url'),
            data.get('is_roundabout'),
            data.get('fatal_victims')
        ))
        conn.commit()
        print(f"Successfully inserted data for URL: {data.get('url')}")
    except sqlite3.IntegrityError:
        print(f"URL already exists in database: {data.get('url')}")
    finally:
        conn.close()

def main():
    create_database()

    with open('urls.txt', 'r') as f:
        urls = f.read().splitlines()

    total_processed = 0

    for url in urls:
        if 'marechal-candido-rondon' not in url.lower():
            print(f"Skipping: {url} (does not contain 'marechal-candido-rondon')")
            continue

        print(f"Processing: {url}")
        article_content = fetch_article_content(url)
        if article_content:
            json_result = process_with_claude(article_content, url)
            if json_result:
                try:
                    parsed_json = json.loads(json_result)
                    if parsed_json:  # Check if the parsed JSON is not empty
                        insert_into_database(parsed_json)
                        total_processed += 1
                        print(f"Successfully processed and inserted data for {url}")
                    else:
                        print(f"Skipping: {url} (not a traffic accident article)")
                except json.JSONDecodeError:
                    print(f"Error parsing JSON for {url}")
            else:
                print(f"No valid JSON returned for {url}")
        else:
            print(f"No article content found for {url}")
        time.sleep(1)  # Be polite to both the article server and Claude API

    print(f"Processed {total_processed} articles. Results saved to articles.db")

if __name__ == "__main__":
    main()
