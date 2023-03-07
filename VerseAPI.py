import requests
from bs4 import BeautifulSoup
from data.Verse import Verse

class WebScaper():
    def Search(query):
        try:
            request = requests.get(
            f'https://ilibrary.ru/text/{query}/p.1/index.html')
            soup = BeautifulSoup(request.content, 'html.parser')
            fullTitle = str(soup.find('title'))[7:-8]
            if fullTitle:
                author = '. '.join(fullTitle.split('. ')[0:3])
                title = '. '.join(fullTitle.split('. ')[3:-1])
                text = []
                for string in soup.find_all('span', class_="vl"):
                    text.append(str(string).split('<span class="i1"></span>')[1].split('<span class="i2">')[0].strip())
                return Verse(author, title, text)
            else:
                return "Простите, но такого стихотворения нет в базе."
        except requests.exceptions.InvalidURL:
            print("Неверно указан адрес сервера")

