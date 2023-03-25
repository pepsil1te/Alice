from alice_scripts import Skill, request, say, suggest
from VerseAPI import WebScraper
from textFormatter import formatAsPlainText, decorateParagraph
from data.Verse import Verse
import sys
skill = Skill(__name__)


@skill.script
def start():
    # Приветствие
    isRunning = True
    yield say('Привет! Это навык поможет тебе выучить стихотворение. Назови любое, и мы можем начать!')
    while(isRunning):
        getVerse(handleVoiceInput(request).command)
    yield say('Пока, хорошего дня!')
    return


def handleVoiceInput(voiceInput):
    word = voiceInput.command.lower()
    if word == "помощь":
        yield say("На данный момент навык имеет следующие комманды: ")
        yield say("""Скажите "Помощь", чтобы узнать список доступных комманд""")
        yield say("""Скажите "Что ты умеешь", чтобы узнать информацию о навыке""")
        # повтори
        yield say("""Скажите "Стоп", чтобы завершить работу навыка и выйти""")
        handleVoiceInput(handleVoiceInput(input()))
    elif word == "что ты умеешь":
        yield say('''Привет, я - Мир Стихов, навык для изучения стихов с помощью моей подруги, голосового помощника Алисы. Со мной и моей помощью ты можешь легко выучить стих к уроку литературы, а также прокачать свою память!''')
        handleVoiceInput(handleVoiceInput(input()))
    elif word == "стоп":
        yield say("Спасибо за использование нашего навыка. До свидания!")
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
        yield say("Какой из этих двух вы хотите выучить? Назовите номер")
        numberOfVerse = handleVoiceInput(request).command
        while not ((numberOfVerse.matches(r'\d+') and 0 < int(numberOfVerse.command) <= len(response))):
            readVerseList(response)
            yield say("Какой из этих стихов вы хотите выучить? Назовите номер")
            numberOfVerse = handleVoiceInput(request).command
        verse = WebScraper.GetVerseById(response[int(numberOfVerse) - 1])
    else:
        yield say(f"Произошла ошибка: {response}")
        yield say('Давайте попробуем ещё раз!')
        return
    readVerse(verse)
    yield say("Хотите выучить данное стихотворение?", suggest('Да', 'Нет'))
    if handleVoiceInput(request).has_lemmas('да', 'давай', 'хорошо'):
        if learnVerse(verse):
            yield say("Отлично, у вас получилось. Хотите попробовать снова?", suggest('Да', 'Нет'))
            if handleVoiceInput(request).has_lemmas('да', 'давай', 'хорошо'):
                yield say("Хорошо, назовите новое стихотворение!")
                return
            else:
                isRunning = False
                return
        else:
            yield say("Мне очень жаль, что у вас не получилось выучить. Может, выучим какой нибудь другой стих?", suggest('Да', 'Нет'))
            if handleVoiceInput(request).has_lemmas('да', 'давай', 'хорошо'):
                return
            else:
                yield say('Ладно, до свидания!')
                isRunning = False
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
        if len(text) != 1 and len(text[paragraph]) != 1:
            yield say(f"Строфа номер {paragraph + 1}")
            yield say(decorateParagraph(text[paragraph]))
        yield say("Начинаем учить строфу!")  # варианты
        learnParagraph(text[paragraph])
        learnedParagraphs.append(text[paragraph])
        if paragraph != 0:
            chances = 5
            yield say(f"Теперь соединим этот строфу с предыдущими. Повторяйте: {' '.join(learnedParagraphs)}")
            while formatAsPlainText(handleVoiceInput(request).command).lower() != formatAsPlainText(' '.join(learnedParagraphs)).lower():
                yield say(f"Простите, но, похоже, вы допустили ошибку. Давайте заново: {' '.join(learnedParagraphs)}")
                chances -= 1
                if chances > 0:
                    yield say(f"Оставшееся количество попыток повторить все выученные строфы: {chances}. Когда попытки закончатся, придётся заново учить стихотворение")
                else:
                    yield say("К сожалению, попытки повторить выученные строфы кончились. Хотите выучить стих заново?", suggest('Да', 'Нет'))
                    if handleVoiceInput(request).has_lemmas('да', 'давай', 'хорошо'):
                        learnVerse(verse)
                    else:
                        return False
    return True


def learnParagraph(paragraph):
    requiredLine = ""
    for line in range(len(paragraph)):
        yield say(paragraph[line])
        # Просим повторить
        yield say('Теперь ваша очередь!')
        # Если не так - повторим while
        while formatAsPlainText(handleVoiceInput(request).command).lower() != formatAsPlainText(paragraph[line]).lower():
            yield say('Простите, кажется, в вашей строке есть ошибка, повторите ещё раз!')
            yield say(f"Повторяйте за мной: {paragraph[line]}")
        requiredLine += paragraph[line] + ' '
        if line != 0:
            yield say("Теперь соединим эту строчку с предыдущими. Повторяйте: ")
            yield say(f"{decorateParagraph(paragraph[:line + 1])}")
            while formatAsPlainText(handleVoiceInput(request).command).lower() != formatAsPlainText(requiredLine).lower():
                yield say("Простите, но, похоже, вы допустили ошибку. Давайте заново:")
                yield say(f"{decorateParagraph(paragraph[:line + 1])}")
    return
