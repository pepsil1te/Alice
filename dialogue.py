from alice_scripts import Skill, request, say, suggest
from VerseAPI import WebScraper
from textFormatter import removePunctuation, decorateParagraph
from data.Verse import Verse
skill = Skill(__name__)


@skill.script
def start():
    # Приветствие
    isRunning = True
    yield say('Привет! Это навык поможет тебе выучить стихотворение. Назови любое, и мы можем начать!')
    while(isRunning):
        getVerse(request.command)
    yield say('Пока, хорошего дня!')


def getVerse(request):
    global isRunning
    response = WebScraper.GetVerseByText(request)
    if isinstance(response, Verse):
        verse = response
    elif isinstance(response, list):
        readVerseList(response)
        yield say("Какой из этих двух вы хотите выучить? Назовите номер")
        numberOfVerse = request.command
        while ("повтори" in numberOfVerse.lower() or not ((numberOfVerse.isdigit() and int(numberOfVerse) <= len(response)))):
            readVerseList(response)
            yield say("Какой из этих стихов вы хотите выучить? Назовите номер")
            numberOfVerse = request.command
        verse = WebScraper.GetVerseById(response[int(numberOfVerse) - 1])
    else:
        yield say(f"Произошла ошибка: {response}")
        yield say('Давайте попробуем ещё раз!')
        return
    readVerse(verse)
    yield say("Хотите выучить данное стихотворение?")
    if "да" in request.command:
        if learnVerse(verse):
            yield say("Отлично, у вас получилось. Хотите попробовать снова?")
            if "да" in request.command.lower().split():
                return True
            else:
                isRunning = False
                return
        else:
            yield say(
                "Очень жаль, что у вас не получилось выучить. Может, попробуем запомнить его ещё раз?")
            if "да" in request.command.lower().split():
                getVerse(request)
            else:
                yield say('Хорошо, тогда назовите другое стихотворение')
                return
    else:
        yield say("Хорошо, тогда назовите другое стихотворение")
        return


def readVerseList(verseList):
    for verseId in range(len(verseList)):
        verse = WebScraper.GetVerseById(verseList[verseId])
        if isinstance(verse, Verse):
            yield say(f"Стих номер {verseId + 1}")
            yield say(f"{verse.author} {verse.title}")
    return


def readVerse(verse):
    yield say(verse)
    return


def learnVerse(verse):
    text = verse.text
    learnedParagraphs = []
    for paragraph in range(len(text)):
        yield say(f"Строфа номер {paragraph + 1}")
        learnParagraph(text[paragraph])
        learnedParagraphs.append(text[paragraph])
        if paragraph != 0:
            chances = 5
            yield say(f"Теперь соединим этот строфу с предыдущими. Повторяйте: {' '.join(learnedParagraphs)}")
            while removePunctuation(request.command).lower() != removePunctuation(' '.join(learnedParagraphs)).lower():
                yield say(f"Простите, но, похоже, вы допустили ошибку. Давайте заново: {' '.join(learnedParagraphs)}")
                chances -= 1
                if chances > 0:
                    yield say(f"Оставшееся количество попыток повторить все выученные строфы: {chances}. Когда попытки закончатся, придётся заново учить стихотворение")
                else:
                    yield say("К сожалению, попытки повторить выученные строфы кончились. Хотите выучить стих заново?")
                    if "да" in request.command.lower().split():
                        learnVerse(verse)
                    else:
                        yield say("Хорошо, тогда назовите другое стихотворение")
                        return True
    return True


def learnParagraph(paragraph):
    requiredLine = ""
    for line in range(len(paragraph)):
        yield say(paragraph[line])
        # Просим повторить
        yield say('Теперь ваша очередь!')
        # Если не так - повторим while
        while removePunctuation(request.command).lower() != removePunctuation(paragraph[line]).lower():
            yield say('Простите, кажется, в вашей строке есть ошибка, повторите ещё раз!')
            yield say(f"Повторяйте за мной: {paragraph[line]}")
        requiredLine += paragraph[line] + ' '
        if line != 0:
            yield say("Теперь соединим эту строчку с предыдущими. Повторяйте: ")
            yield say(f"{decorateParagraph(paragraph[:line + 1])}")
            while removePunctuation(request.command).lower() != removePunctuation(requiredLine).lower():
                yield say("Простите, но, похоже, вы допустили ошибку. Давайте заново:")
                yield say(f"{decorateParagraph(paragraph[:line + 1])}")
    return

start()
