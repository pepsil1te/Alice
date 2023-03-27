from alice_scripts import Skill, request, say, suggest
from VerseAPI import WebScraper
from textFormatter import formatAsPlainText, decorateParagraph
from data.Verse import Verse
import sys


skill = Skill(__name__)


@skill.script
def start():
    global verseWasLearned, inputRequest
    # Приветствие
    verseWasLearned = False
    inputRequest = ''
    yield say('Привет! Это навык поможет тебе выучить стихотворение. Назови любое, и мы можем начать!', 'Здравствуй! Этот навык поможет тебе выучить стихи. Скажи название любого и мы начинаем!', 'Приветствую! Я могу помочь тебе запомнить любое стихотворение. Назови любое!',
            suggest('А.С. Пушкин "Я вас любил"', 'Есенин "Береза"'),
            tts="""<speaker audio='dialogs-upload/56bbf307-260d-4267-bcff-778a59f85ff5/b3773883-8c32-438d-853f-b5a843d60188.opus'>""")
    while(True):
        yield from handleVoiceInput(request)
        yield from getVerse(inputRequest.command)


def handleVoiceInput(voiceInput):
    global inputRequest
    word = voiceInput.command.lower()
    if word in ["помощь", "помоги"]:
        yield say("""На данный момент навык имеет следующие комманды: \nСкажите "Помощь", чтобы узнать список доступных комманд\nСкажите "Что ты умеешь" или "Умения", чтобы узнать информацию о навыке\nСкажите "Стоп", чтобы завершить работу навыка и выйти""")
        yield from handleVoiceInput(request)
    elif word in ["что ты умеешь", "умения"]:
        yield say('''Привет, я - Мир Стихов, навык для изучения стихов с помощью моей подруги, голосового помощника Алисы. Со мной и моей помощью ты можешь легко выучить стих к уроку литературы, а также прокачать свою память!''')
        yield from handleVoiceInput(request)
    elif word == "стоп":
        yield say("Спасибо за использование нашего навыка. До свидания!",'Благодарим вас за использование нашего навыка. Хорошего дня!','Было приятно помочь вам. До свидания!', end_session='true')
    else:
        inputRequest = voiceInput
        return


def getVerse(requestedVerse):
    global inputRequest, verseWasLearned
    response = WebScraper.GetVerseByText(requestedVerse)
    if isinstance(response, Verse):
        verse = response
    elif isinstance(response, list):
        yield say(f"{readVerseList(response)}\nКакое из этих стихотворений вы хотите выучить? Назовите номер", tts="""<speaker audio='dialogs-upload/56bbf307-260d-4267-bcff-778a59f85ff5/b3773883-8c32-438d-853f-b5a843d60188.opus'>""")
        yield from handleVoiceInput(request)
        numberOfVerse = inputRequest
        while not ((numberOfVerse.matches(r'\d+') and 0 < int(numberOfVerse.command) <= len(response))):
            yield say(f"{readVerseList(response)}\nПохоже, вы ввели неправильный номер. Какой из этих стихов вы хотите выучить? Назовите только цифру",
                      tts='''<speaker audio='dialogs-upload/56bbf307-260d-4267-bcff-778a59f85ff5/1c5585e1-b08a-47ca-ae3e-38ba58d06e3c.opus'>''')
            yield from handleVoiceInput(request)
            numberOfVerse = inputRequest
        verse = WebScraper.GetVerseById(response[int(numberOfVerse.command) - 1])
    else:
        yield say(f"Произошла ошибка: {response}\nДавайте попробуем ещё раз!", tts="""<speaker audio='dialogs-upload/56bbf307-260d-4267-bcff-778a59f85ff5/407cee6c-c754-4f97-b898-fb9aaa55693d.opus'>""")
        return
    yield from readVerse(verse)
    yield from handleVoiceInput(request)
    if inputRequest.has_lemmas('да', 'давай', 'хорошо', 'ок', 'ok'):
        yield from learnVerse(verse)
        if (verseWasLearned):
            yield say("Отлично, у вас получилось. Хотите попробовать снова?", suggest('Да', 'Нет'), tts="<speaker audio='dialogs-upload/56bbf307-260d-4267-bcff-778a59f85ff5/4261b974-0dee-4c50-ad08-9828dcec6b3b.opus'>")
            verseWasLearned = False
            yield from handleVoiceInput(request)
            if inputRequest.has_lemmas('да', 'давай', 'хорошо', 'ок', 'ok'):
                yield say("Хорошо, назовите новое стихотворение!", 'Прекрасно, можете назвать другое стихотворение?', 'Хорошо, давайте выберем другое стихотворение для изучения.', 'Окей, давайте выберем новое стихотворение', tts="""<speaker audio='dialogs-upload/56bbf307-260d-4267-bcff-778a59f85ff5/b3773883-8c32-438d-853f-b5a843d60188.opus'>""")
                return
            else:
                yield say('Ладно, до свидания!', 'Хорошо, пока!','Окей, до встречи!','До скорой встречи!', end_session='true')
                sys.exit()
        else:
            return
    else:
        yield say("Хорошо, назовите новое стихотворение!", 'Прекрасно, можете назвать другое стихотворение?', 'Хорошо, давайте выберем другое стихотворение для изучения.', 'Окей, давайте выберем новое стихотворение', tts="""<speaker audio='dialogs-upload/56bbf307-260d-4267-bcff-778a59f85ff5/b3773883-8c32-438d-853f-b5a843d60188.opus'>""")
        return


def readVerseList(verseList):
    response = ''
    for verseId in range(len(verseList)):
        verse = WebScraper.GetVerseById(verseList[verseId])
        if isinstance(verse, Verse):
            response += f"Стих номер {verseId + 1}\n{verse.author} {verse.title}" + '\n'
    return response.strip()

def readVerse(verse):
    if len(str(verse)) + 40 <= 1024:
        yield say(f"""{str(verse)}\nХотите выучить данное стихотворение?""", suggest('Да', 'Нет'), tts="""<speaker audio='dialogs-upload/56bbf307-260d-4267-bcff-778a59f85ff5/b3773883-8c32-438d-853f-b5a843d60188.opus'>""")
    else:
        yield say(f"""Ой, какое большое стихотворение! Читать его - долгое занятие, давайте сразу начнём учить по строфам. \nХотите выучить данное стихотворение?""", suggest('Да', 'Нет'), tts="""<speaker audio='dialogs-upload/56bbf307-260d-4267-bcff-778a59f85ff5/b3773883-8c32-438d-853f-b5a843d60188.opus'>""")
    return


def learnVerse(verse):
    global verseWasLearned, inputRequest
    text = verse.text
    learnedParagraphs = []
    for paragraph in range(len(text)):
        if len(text) != 1 and len(text[paragraph]) != 1:
            yield say(f"Строфа номер {paragraph + 1}\n{decorateParagraph(text[paragraph])}\nНачнём учить строфу?", suggest('Да', 'Нет'), tts="""<speaker audio='dialogs-upload/56bbf307-260d-4267-bcff-778a59f85ff5/b3773883-8c32-438d-853f-b5a843d60188.opus'>""")  # варианты
            yield from handleVoiceInput(request)
            while not (inputRequest).has_lemmas('да', 'давай', 'хорошо', 'ок', 'ok'):
                yield say(f"Строфа номер {paragraph + 1}\n{decorateParagraph(text[paragraph])})\nНачнём учить строфу?", suggest('Да', 'Нет'), tts="""<speaker audio='dialogs-upload/56bbf307-260d-4267-bcff-778a59f85ff5/b3773883-8c32-438d-853f-b5a843d60188.opus'>""")  # варианты
                yield from handleVoiceInput(request)
        yield from learnParagraph(text[paragraph])
        learnedParagraphs.append(' '.join(text[paragraph]))
        if paragraph != 0:
            chances = 5
            # !!! Слишком большой текст для повторения !!!
            if len(" ".join(learnedParagraphs)) < 960:
                yield say(f"Теперь соединим этот строфу с предыдущими. Повторяйте: {decorateParagraph(learnedParagraphs)}", tts="""<speaker audio='dialogs-upload/56bbf307-260d-4267-bcff-778a59f85ff5/b3773883-8c32-438d-853f-b5a843d60188.opus'>""")
                yield from handleVoiceInput(request)
                inputParagraphs = inputRequest.command
            else:
                yield say("Теперь соединим этот строфу с предыдущими. Вы обладаете феноменальной памятью, если запомнили предыдущие строфы, даже я их уже успел забыть, ведь этот текст слишком большой. Если хотите - назовите номер строфы, я постараюсь вспомнить её и повторить",'Теперь давайте соединим эту строфу с предыдущими. Вы настоящий мастер запоминания, если вы уже запомнили предыдущие строфы, ведь это было довольно длинное стихотворение. Если вы хотите, вы можете назвать номер строфы, и я постараюсь вспомнить ее и повторить.')
                yield from handleVoiceInput(request)
                numberOfParagraph = inputRequest
                while numberOfParagraph.matches(r'\d+'):
                    if 0 < int(numberOfParagraph.command) <= paragraph + 1:
                        yield say(f"Строфа номер {numberOfParagraph.command}\n{decorateParagraph(text[int(numberOfParagraph.command) - 1])})\nЕсли вы готовы, можете отвечать все выученные строфы. Если требуется снова повторить какую либо строфу - назовите номер")
                    else:
                        yield say("Простите, но вы ввели некорректный номер строфы, возможно, вы ещё не учили её. Пожалуйста, назовите число - порядковый номер строфы, или можете начинать отвечать все строфы, которые вы выучили",
                                  tts='''<speaker audio='dialogs-upload/56bbf307-260d-4267-bcff-778a59f85ff5/1c5585e1-b08a-47ca-ae3e-38ba58d06e3c.opus'>''')
                    yield from handleVoiceInput(request)
                    numberOfParagraph = inputRequest
                inputParagraphs = numberOfParagraph.command
            while formatAsPlainText(inputParagraphs).lower() != formatAsPlainText(' '.join(learnedParagraphs)).lower():
                chances -= 1
                if chances > 0:
                    if len(" ".join(learnedParagraphs)) < 900:
                        yield say(f"Простите, но, похоже, вы допустили ошибку. Оставшееся количество попыток повторить все выученные строфы: {chances}. Когда попытки закончатся, придётся заново учить стихотворение. \
                                  Попробуйте ещё раз связать все выученные строфы, если хотите, можете назвать номер строфы и я повторю её",
                                  tts='''<speaker audio='dialogs-upload/56bbf307-260d-4267-bcff-778a59f85ff5/1c5585e1-b08a-47ca-ae3e-38ba58d06e3c.opus'>''')
                        yield from handleVoiceInput(request)
                        numberOfParagraph = inputRequest
                        while numberOfParagraph.matches(r'\d+'):
                            if 0 < int(numberOfParagraph.command) <= paragraph + 1:
                                yield say(f"Строфа номер {numberOfParagraph.command}\n{decorateParagraph(text[int(numberOfParagraph.command) - 1])})\nЕсли вы готовы, можете отвечать все выученные строфы. Если требуется снова повторить какую либо строфу - назовите номер", tts="""< speaker audio='dialogs-upload/56bbf307-260d-4267-bcff-778a59f85ff5/b3773883-8c32-438d-853f-b5a843d60188.opus'>""")
                            else:
                                yield say("Простите, но вы ввели некорректный номер строфы, возможно, вы ещё не учили её. Пожалуйста, назовите число - порядковый номер строфы, или можете начинать отвечать все строфы, которые вы выучили",
                                          tts='''<speaker audio='dialogs-upload/56bbf307-260d-4267-bcff-778a59f85ff5/1c5585e1-b08a-47ca-ae3e-38ba58d06e3c.opus'>''')
                            yield from handleVoiceInput(request)
                            numberOfParagraph = inputRequest
                        inputParagraphs = numberOfParagraph.command
                    else:
                        yield say(f"Простите, но, похоже, вы допустили ошибку. Оставшееся количество попыток повторить все выученные строфы: {chances}. Когда попытки закончатся, придётся заново учить стихотворение. Давайте заново: {decorateParagraph(learnedParagraphs)}",
                                  tts='''<speaker audio='dialogs-upload/56bbf307-260d-4267-bcff-778a59f85ff5/1c5585e1-b08a-47ca-ae3e-38ba58d06e3c.opus'>''')
                        yield from handleVoiceInput(request)
                        inputParagraphs = inputRequest.command
                else:
                    yield say("К сожалению, попытки повторить выученные строфы кончились. Хотите выучить стих заново?",'К сожалению, вы исчерпали свои попытки воспроизвести выученные строфы. Желаете начать заново?', suggest('Да', 'Нет'), 
                              tts='''<speaker audio='dialogs-upload/56bbf307-260d-4267-bcff-778a59f85ff5/1c5585e1-b08a-47ca-ae3e-38ba58d06e3c.opus'>''')
                    yield from handleVoiceInput(request)
                    if (inputRequest).has_lemmas('да', 'давай', 'хорошо', 'ок', 'ok'):
                        yield from learnVerse(verse)
                    else:
                        yield say("Мне очень жаль, что у вас не получилось выучить. Может, выучим какой нибудь другой стих?",'Мне жаль, что вы не смогли запомнить этот стих. Попробуем с другим?', suggest('Да', 'Нет'))
                        yield from handleVoiceInput(request)
                        if inputRequest.has_lemmas('да', 'давай', 'хорошо', 'ок', 'ok'):
                            yield say("Хорошо, назовите новое стихотворение!", 'Прекрасно, можете назвать другое стихотворение?', 'Хорошо, давайте выберем другое стихотворение для изучения.', 'Окей, давайте выберем новое стихотворение', tts="""<speaker audio='dialogs-upload/56bbf307-260d-4267-bcff-778a59f85ff5/b3773883-8c32-438d-853f-b5a843d60188.opus'>""")
                            return
                        else:
                            yield say('Ладно, до свидания!', 'Хорошо, пока!','Окей, до встречи!','До скорой встречи!', end_session='true')
                            sys.exit()
    verseWasLearned = True
    return


def learnParagraph(paragraph):
    global inputRequest
    requiredLine = ""
    for line in range(len(paragraph)):
        yield say(f"{paragraph[line]}\nТеперь ваша очередь!", f"{paragraph[line]}\nТеперь пора вам показать, что вы умеете.", f"{paragraph[line]}\nВаша очередь!", f"{paragraph[line]}\nТеперь вы!", tts="""<speaker audio='dialogs-upload/56bbf307-260d-4267-bcff-778a59f85ff5/b3773883-8c32-438d-853f-b5a843d60188.opus'>""")
        # Если не так - повторим while
        yield from handleVoiceInput(request)
        while formatAsPlainText(inputRequest.command).lower() != formatAsPlainText(paragraph[line]).lower():
            yield say(f"Простите, кажется, в вашей строке есть ошибка, давайте ещё раз!\nПовторяйте за мной: {paragraph[line]}",f"Извините, в строке обнаружена ошибка. Давайте еще раз попробуем!\nСкажи за мной: {paragraph[line]}",
                      tts='''<speaker audio='dialogs-upload/56bbf307-260d-4267-bcff-778a59f85ff5/1c5585e1-b08a-47ca-ae3e-38ba58d06e3c.opus'>''')
            yield from handleVoiceInput(request)
        requiredLine += paragraph[line] + ' '
        if line != 0:
            yield say(f"Теперь соединим эту строчку с предыдущими. Повторяйте:\n{decorateParagraph(paragraph[:line + 1])}",f"Перейдем к следующей строке и свяжем ее с предыдущей. Давайте повторим:\n{decorateParagraph(paragraph[:line + 1])}")
            yield from handleVoiceInput(request)
            while formatAsPlainText(inputRequest.command).lower() != formatAsPlainText(requiredLine).lower():
                yield say(f"Простите, но, похоже, вы допустили ошибку. Давайте заново:\n{decorateParagraph(paragraph[:line + 1])}",f"Простите, но здесь есть ошибка. Давайте сделаем это заново:\n{decorateParagraph(paragraph[:line + 1])}",
                          tts='''<speaker audio='dialogs-upload/56bbf307-260d-4267-bcff-778a59f85ff5/1c5585e1-b08a-47ca-ae3e-38ba58d06e3c.opus'>''')
                yield from handleVoiceInput(request)
    return

if __name__ == '__main__':
    skill.run()
