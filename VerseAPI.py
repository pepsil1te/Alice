import requests
from bs4 import BeautifulSoup
from data.Verse import Verse

class WebScaper():
    def Search(query):
        request = requests.get(
            f'https://ilibrary.ru/text/{query}/p.1/index.html')
        soup = BeautifulSoup(request.content, 'html.parser')
        fullTitle = str(soup.find('title'))[7:-8]
        if fullTitle:
            title = fullTitle[fullTitle.find("«"):fullTitle.find("»")]
            author = fullTitle[:fullTitle.find("«")]
            text = []
            for string in soup.find_all('span', class_="vl"):
                text.append(str(string).split('<span class="vl"><span class="i1"></span>')[1].split('<span class="i2">')[0])
            return Verse(author, title, text)
        else:
            return "Простите, но такого стихотворения нет в базе."