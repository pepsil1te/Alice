from alice_scripts import Skill, request, say, suggest
from VerseAPI import WebScaper
from data import Verse
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
    response = WebScaper.GetVerseByText(request)
    if isinstance(response, Verse):
        print(response)
    elif isinstance(response, list):
        readVerseList(response)
        yield say("Какой из этих двух вы хотите выучить? Назовите номер")
        while "повтори" in request.command.lower() or not (isinstance(request.command, int) and request.command - 1 <= len(response)):
            readVerseList(response)
            yield say("Какой из этих двух вы хотите выучить? Назовите номер")
        verse = response[request.command - 1]
    else:
        yield say(f"Произошла ошибка: {response}")
        yield say('Давайте попробуем ещё раз!')
        return
    readVerse(verse)
    yield say("Хотите выучить данное стихотворение?")
    if "да" in request.command.lower():
        if learnVerse(verse):
            yield say("Отлично, у вас получилось. Хотите попробовать снова?")
            if "да" in request.command.lower():
                return True
            else:
                isRunning = False
                return
        else:
            yield say("Очень жаль, что у вас не получилось выучить. Может, попробуем запомнить его ещё раз?")
            if "да" in request.command.lower():
                getVerse(request)
            else:
                yield say('Хорошо, тогда назовите другое стихотворение')
                return
    else:
        yield say("Хорошо, тогда назовите другое стихотворение")
        return

def readVerseList(verseList):
    for verseId in range(len(verseList)):
        verse = WebScaper.GetVerseById(verseList[verseId])
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
        learnParagraph(paragraph)
        learnedParagraphs.append(paragraph)
        if paragraph != 0:
            chances = 5
            yield say(f"Теперь соединим этот строфу с предыдущими. Повторяйте: {' '.join(learnedParagraphs)}")
            while request.command != ' '.join(learnedParagraphs):
                yield say(f"Простите, но, похоже, вы допустили ошибку. Давайте заново: {' '.join(learnedParagraphs)}")
                chances -= 1
                if chances > 0:
                    yield say(f"Оставшееся количество попыток повторить все выученные строфы: {chances}. Когда попытки закончатся, придётся заново учить стихотворение")
                else:
                    yield say("К сожалению, попытки повторить выученные строфы кончились. Хотите выучить стих заново?")
                    if "да" in request.command.lower():
                        learnVerse(verse)
                    else:
                        yield say("Хорошо, тогда назовите другое стихотворение")
                        return True
    return True

def learnParagraph(paragraph):
    requiredLine = ""
    for line in range(len(paragraph)):
        yield say(f"Строка номер {line + 1}: {paragraph[line]}")
        # Просим повторить
        yield say('Теперь ваша очередь!')
        # Если не так - повторим while
        while request.command != line:
            yield say('Простите, кажется, в вашей строке есть ошибка, повторите ещё раз!')
            yield say(f"Повторяйте за мной: {line}")
        requiredLine += paragraph[line] + ' '
        if line != 0:
            yield say(f"Теперь соединим эту строчку с предыдущими. Повторяйте: {paragraph[:line]}")
            while request.command != requiredLine.strip():
                yield say(f"Простите, но, похоже, вы допустили ошибку. Давайте заново: {requiredLine}")
    return

