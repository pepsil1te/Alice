from alice_scripts import Skill, request, say, suggest
from VerseAPI import WebScraper
from textFormatter import removePunctuation, decorateParagraph
from data.Verse import Verse
skill = Skill(__name__)


@skill.script
def start():
    # Приветствие
    isRunning = True
    print('Привет! Это навык поможет тебе выучить стихотворение. Назови любое, и мы можем начать!')
    while(isRunning):
        getVerse(input())
    print('Пока, хорошего дня!')


def getVerse(request):
    global isRunning
    response = WebScraper.GetVerseByText(request)
    if isinstance(response, Verse):
        verse = response
    elif isinstance(response, list):
        readVerseList(response)
        print("Какой из этих двух вы хотите выучить? Назовите номер")
        numberOfVerse = input()
        while ("повтори" in numberOfVerse.lower() or not ((numberOfVerse.isdigit() and int(numberOfVerse) <= len(response)))):
            readVerseList(response)
            print("Какой из этих стихов вы хотите выучить? Назовите номер")
            numberOfVerse = input()
        verse = WebScraper.GetVerseById(response[int(numberOfVerse) - 1])
    else:
        print(f"Произошла ошибка: {response}")
        print('Давайте попробуем ещё раз!')
        return
    readVerse(verse)
    print("Хотите выучить данное стихотворение?")
    if "да" in input():
        if learnVerse(verse):
            print("Отлично, у вас получилось. Хотите попробовать снова?")
            if "да" in input().lower().split():
                return True
            else:
                isRunning = False
                return
        else:
            print(
                "Очень жаль, что у вас не получилось выучить. Может, попробуем запомнить его ещё раз?")
            if "да" in input().lower().split():
                getVerse(request)
            else:
                print('Хорошо, тогда назовите другое стихотворение')
                return
    else:
        print("Хорошо, тогда назовите другое стихотворение")
        return


def readVerseList(verseList):
    for verseId in range(len(verseList)):
        verse = WebScraper.GetVerseById(verseList[verseId])
        if isinstance(verse, Verse):
            print(f"Стих номер {verseId + 1}")
            print(f"{verse.author} {verse.title}")
    return


def readVerse(verse):
    print(verse)
    return


def learnVerse(verse):
    text = verse.text
    learnedParagraphs = []
    for paragraph in range(len(text)):
        print(f"Строфа номер {paragraph + 1}")
        learnParagraph(text[paragraph])
        learnedParagraphs.append(text[paragraph])
        if paragraph != 0:
            chances = 5
            print(
                f"Теперь соединим этот строфу с предыдущими. Повторяйте: {' '.join(learnedParagraphs)}")
            while removePunctuation(input()).lower() != removePunctuation(' '.join(learnedParagraphs)).lower():
                print(
                    f"Простите, но, похоже, вы допустили ошибку. Давайте заново: {' '.join(learnedParagraphs)}")
                chances -= 1
                if chances > 0:
                    print(
                        f"Оставшееся количество попыток повторить все выученные строфы: {chances}. Когда попытки закончатся, придётся заново учить стихотворение")
                else:
                    print(
                        "К сожалению, попытки повторить выученные строфы кончились. Хотите выучить стих заново?")
                    if "да" in input().lower().split():
                        learnVerse(verse)
                    else:
                        print("Хорошо, тогда назовите другое стихотворение")
                        return True
    return True


def learnParagraph(paragraph):
    requiredLine = ""
    for line in range(len(paragraph)):
        print(paragraph[line])
        # Просим повторить
        print('Теперь ваша очередь!')
        # Если не так - повторим while
        while removePunctuation(input()).lower() != removePunctuation(paragraph[line]).lower():
            print('Простите, кажется, в вашей строке есть ошибка, повторите ещё раз!')
            print(f"Повторяйте за мной: {paragraph[line]}")
        requiredLine += paragraph[line] + ' '
        if line != 0:
            print("Теперь соединим эту строчку с предыдущими. Повторяйте: ")
            print(f"{decorateParagraph(paragraph[:line + 1])}")
            while removePunctuation(input()).lower() != removePunctuation(requiredLine).lower():
                print("Простите, но, похоже, вы допустили ошибку. Давайте заново:")
                print(f"{decorateParagraph(paragraph[:line + 1])}")
    return

start()
