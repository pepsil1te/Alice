from VerseAPI import WebScraper
from textFormatter import formatAsPlainText, decorateParagraph
from data.Verse import Verse
import sys


def start():
    # Приветствие
    isRunning = True
    print('Привет! Это навык поможет тебе выучить стихотворение. Назови любое, и мы можем начать!')
    while(isRunning):
        getVerse(handleVoiceInput(input()))
    print('Пока, хорошего дня!')

def handleVoiceInput(voiceInput):
    word = voiceInput.lower()
    if word == "помощь":
        print("На данный момент навык имеет следующие комманды: ")
        print("""Скажите "Помощь", чтобы узнать список доступных комманд""")
        print("""Скажите "Что ты умеешь", чтобы узнать информацию о навыке""")
        # повтори
        print("""Скажите "Стоп", чтобы завершить работу навыка и выйти""")
        handleVoiceInput(handleVoiceInput(input()))
    elif word == "что ты умеешь":
        print('''Привет, я - Мир Стихов, навык для изучения стихов с помощью моей подруги, голосового помощника Алисы. Со мной и моей помощью ты можешь легко выучить стих к уроку литературы, а также прокачать свою память!''')
        handleVoiceInput(handleVoiceInput(input()))
    elif word == "стоп":
        print("Спасибо за использование нашего навыка. До свидания!")
        sys.exit()
    else:
        return voiceInput

def getVerse(requestedVerse):
    global isRunning
    response = WebScraper.GetVerseByText(requestedVerse)
    if isinstance(response, Verse):
        verse = response
    elif isinstance(response, list):
        readVerseList(response)
        print("Какой из этих двух вы хотите выучить? Назовите номер")
        numberOfVerse = handleVoiceInput(input())
        # not request.matches(r'\d+')
        while not ((numberOfVerse.isdigit() and 0 < int(numberOfVerse) <= len(response))):
            readVerseList(response)
            print("Какой из этих стихов вы хотите выучить? Назовите номер")
            numberOfVerse = handleVoiceInput(input())
        verse = WebScraper.GetVerseById(response[int(numberOfVerse) - 1])
    else:
        print(f"Произошла ошибка: {response}")
        print('Давайте попробуем ещё раз!')
        return
    readVerse(verse)
    print("Хотите выучить данное стихотворение?")
    if "да" in handleVoiceInput(input()):
        if learnVerse(verse):
            print("Отлично, у вас получилось. Хотите попробовать снова?")
            if "да" in handleVoiceInput(input()).lower().split():
                print("Хорошо, назовите новое стихотворение!")
                return
            else:
                isRunning = False
                return
        else:
            print("Очень жаль, что у вас не получилось выучить. Может, выучим какой нибудь другой стих?")
            if "да" in handleVoiceInput(input()).lower().split():
                getVerse(requestedVerse)
            else:
                print('Ладно, до свидания!')
                isRunning = False
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
        if len(text) != 1 and len(text[paragraph]) != 1:
            print(f"Строфа номер {paragraph + 1}")
            print(decorateParagraph(text[paragraph]))
        print("Начинаем учить строфу!") # варианты
        learnParagraph(text[paragraph])
        learnedParagraphs.append(text[paragraph])
        if paragraph != 0:
            chances = 5
            print(f"Теперь соединим этот строфу с предыдущими. Повторяйте: {' '.join(learnedParagraphs)}")
            while formatAsPlainText(handleVoiceInput(input())).lower() != formatAsPlainText(' '.join(learnedParagraphs)).lower():
                print(
                    f"Простите, но, похоже, вы допустили ошибку. Давайте заново: {' '.join(learnedParagraphs)}")
                chances -= 1
                if chances > 0:
                    print(f"Оставшееся количество попыток повторить все выученные строфы: {chances}. Когда попытки закончатся, придётся заново учить стихотворение")
                else:
                    print("К сожалению, попытки повторить выученные строфы кончились. Хотите выучить стих заново?")
                    if "да" in handleVoiceInput(input()).lower().split():
                        learnVerse(verse)
                    else:
                        return False
    return True


def learnParagraph(paragraph):
    requiredLine = ""
    for line in range(len(paragraph)):
        print(paragraph[line])
        # Просим повторить
        print('Теперь ваша очередь!')
        # Если не так - повторим while
        while formatAsPlainText(handleVoiceInput(input())).lower() != formatAsPlainText(paragraph[line]).lower():
            print('Простите, кажется, в вашей строке есть ошибка, повторите ещё раз!')
            print(f"Повторяйте за мной: {paragraph[line]}")
        requiredLine += paragraph[line] + ' '
        if line != 0:
            print("Теперь соединим эту строчку с предыдущими. Повторяйте: ")
            print(f"{decorateParagraph(paragraph[:line + 1])}")
            while formatAsPlainText(handleVoiceInput(input())).lower() != formatAsPlainText(requiredLine).lower():
                print("Простите, но, похоже, вы допустили ошибку. Давайте заново:")
                print(f"{decorateParagraph(paragraph[:line + 1])}")
    return

start()