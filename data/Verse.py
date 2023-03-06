class Verse():
    def __init__(self, author, title, text):
        self.author = author
        self.title = title
        self.text = text
    def __str__(self):
        text = '\n'.join(self.text)
        return str(f"{self.author}\n{self.title}\n{text}")
