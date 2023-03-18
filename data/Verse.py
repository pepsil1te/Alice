class Verse():
    def __init__(self, author, title, text):
        self.author = author # str
        self.title = title # str
        self.text = text # list of lists
    def __str__(self):
        text = ""
        for paragraph in self.text:
            text += '\n'.join(paragraph) + '\n'
        return str(f"{self.author}\n{self.title}\n{text.strip()}")
