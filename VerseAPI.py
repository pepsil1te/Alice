import requests
from bs4 import BeautifulSoup
from duckduckgo_search import ddg
from data.Verse import Verse
from textFormatter import removeBrackets, removeBracketsFromLine

class WebScraper():
    def GetVerseById(queryId):
        try:
            request = requests.get(
            f'https://ilibrary.ru/text/{queryId}/p.1/index.html')
            soup = BeautifulSoup(request.content, 'html.parser')
            fullTitle = str(soup.find('title'))[7:-8]
            if fullTitle:
                author = '. '.join(fullTitle.split('. ')[0:3])
                title = '. '.join(fullTitle.split('. ')[3:-1])
                text = []
                for p in str(soup.find_all('span', class_="pmm")).split('<span class="p">'):
                    paragraph = []
                    for string in str(p).split('<span class="vl">')[1:]:
                        line = str(string).split(
                            '<span class="i1"></span>')[1].split('<span class="i2">')[0].strip()
                        line = line.replace(u'\xa0', u' ')
                        if line:
                            paragraph.append(line)
                    if paragraph:
                        text.append(paragraph)
                text = removeBrackets(text)
                return Verse(author, title, text)
            else:
                return "Простите, но такого стихотворения нет в базе."
        except requests.exceptions.InvalidURL:
            return "Неверно указан адрес сервера"

    def SearchForId(queryText):
        results = ddg(queryText, region='ru-ru', safesearch='Off')
        verses = []
        if results:
            for result in results:
                if 'ilibrary.ru' in result['href'] and 'text' in result['href']:
                    verseId = result['href'].split('/')[4]
                    if verseId.isdigit():
                        verseId = int(verseId)
                        if WebScraper.isVerse(verseId):
                            verses.append(verseId)
        if verses:
            if len(verses) == 1:
                return verses[0]
            else:
                uniqueVerses = [verses[0]]
                for i in range (1, len(verses)):
                    if verses[i] != verses[i - 1]:
                        uniqueVerses.append(verses[i])
                if len(uniqueVerses) > 1:
                    return uniqueVerses
                else:
                    return uniqueVerses[0]
        else:
            return "Простите, стихотворение не найдено, возможно, оно слишком большое, или является частью произведения. Пожалуйста, повторите запрос"
    
    def GetVerseByText(queryText):
        verseId = WebScraper.SearchForId(queryText)
        if isinstance(verseId, int):
            return WebScraper.GetVerseById(verseId)
        else:
            return verseId
    
    def isVerse(verseId):
        try:
            request = requests.get(f'https://ilibrary.ru/text/{verseId}/p.1/index.html')
            soup = BeautifulSoup(request.content, 'html.parser')
            for button in soup.find_all('a', class_="bttn"):
                if removeBracketsFromLine(str(button)) == "о тексте/оглавление":
                    return False
            for h3 in soup.find_all("h3"):
                if removeBracketsFromLine(str(h3)).isdigit():
                    return False
            return True
        except:
            return False