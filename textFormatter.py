class TextFormatter():
    def removeBrackets(text):
        for paragraphIndex in range(len(text)):
            paragraph = text[paragraphIndex]
            for lineIndex in range(len(paragraph)):
                line = paragraph[lineIndex]
                bracketsIndexes = []
                for s in range(len(line)):
                    if line[s] == "<":
                        bracketsIndexes.append(s)
                indexToSubtract = 0
                for i in range(len(bracketsIndexes)):
                    indexToSubtract = len(line[bracketsIndexes[i]:line.find(">", bracketsIndexes[i]) + 1])
                    line = line[:bracketsIndexes[i]] + line[line.find(">", bracketsIndexes[i]) + 1:]
                    if i + 1 != len(bracketsIndexes):
                        bracketsIndexes[i + 1] -= indexToSubtract
                        indexToSubtract = 0
                paragraph[lineIndex] = line
            text[paragraphIndex] = paragraph
        return text
