import csv
import sqlite3
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

def create_database():
    conn = sqlite3.connect('marechal_rondon_articles.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS articles
                 (url TEXT PRIMARY KEY,
                  title TEXT,
                  description TEXT,
                  datetime DATETIME,
                  content TEXT,
                  roundabout BOOLEAN,
                  car BOOLEAN,
                  bus BOOLEAN,
                  motorcycle BOOLEAN,
                  bike BOOLEAN,
                  truck BOOLEAN,
                  pedestrian BOOLEAN,
                  electric BOOLEAN)''')
    conn.commit()
    return conn

def fetch_article_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to retrieve article from {url}. Status code: {response.status_code}")
        return None
    return response.content

def parse_datetime(date_string):
    return datetime.strptime(date_string, '%d/%m/%Y %Hh%M')

def check_content_for_keywords(content, keywords):
    return any(keyword in content.lower() for keyword in keywords)

def process_article(row, conn):
    title, description, url = row
    html_content = fetch_article_content(url)
    if html_content is None:
        return

    soup = BeautifulSoup(html_content, 'html.parser')

    content_div = soup.select_one('div.conteudo-interno')
    if content_div is None:
        print(f"Could not find content for article: {url}")
        return

    el = content_div.select_one('div.box-relacionados')
    if el is not None:
        el.decompose()
    el = content_div.select_one('div.box-comentarios')
    if el is not None:
        el.decompose()

    content_div.smooth()
    content = content_div.get_text(strip=True)

    date_element = soup.select_one('div.data-post span')
    if date_element is None:
        print(f"Could not find date for article: {url}")
        return

    article_datetime = parse_datetime(date_element.text.strip())

    roundabout = check_content_for_keywords(content, ['rotatoria', 'rotula', 'rotatória', 'rótula'])
    car = check_content_for_keywords(content, ['carro', 'carros', 'veiculos', 'veículo', 'veículos', 'camioneta', 'camionetas'])
    bus = check_content_for_keywords(content, ['onibus','ônibus'])
    motorcycle = check_content_for_keywords(content, ['moto', 'motocicleta'])
    bike = check_content_for_keywords(content, ['bicicleta', 'ciclista', 'bike'])
    electric = check_content_for_keywords(content, ['eletrico', 'elétrico'])
    truck = check_content_for_keywords(content, ['caminhao', 'caminhão', 'carreta'])
    pedestrian = check_content_for_keywords(content, ['pedestre', 'pedestres'])

    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO articles
                 (url, title, description, datetime, content, roundabout, car, bus, motorcycle, bike, electric, truck, pedestrian)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (url, title, description, article_datetime, content, roundabout, car, bus, motorcycle, bike, electric, truck, pedestrian))
    conn.commit()
    print(f"Processed and stored article: {url}")

def main():
    conn = create_database()

    with open('marechal_rondon_articles.csv', 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row
        for row in reader:
            process_article(row, conn)

    conn.close()
    print("Finished processing all articles.")

if __name__ == "__main__":
    main()
