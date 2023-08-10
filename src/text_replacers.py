# Contains all of the functions used to re-generate text data to help declutter the main script
import colorama
import random
from essential_generators import DocumentGenerator

colorama.init()
generator = DocumentGenerator()


def randomSentence(dataIn: str, **kwargs):
    words = dataIn.split(' ')
    # Filters out NewLine chars
    for word in words:
        if '\n' in word:
            words[words.index(word)] = word.split('\n')

    def getTrueLength(listIn: list) -> int:
        trueCount = 0
        for word in listIn:
            if isinstance(word, str):
                trueCount += 1
            elif isinstance(word, list):
                trueCount += getTrueLength(word)
            else:
                print("Wasn't a string or list")
                continue
        return trueCount
    refreshCache = random.randint(0, 10000)

    if refreshCache == 3751:
        generator.init_sentence_cache()
        generator.init_word_cache()
    else:
        pass

    wordLength = getTrueLength(words)
    if wordLength < 3:
        if wordLength == 1:
            generatedText = generator.text_generator.gen_word()
        else:
            generatedText = generator.gen_sentence(min_words=wordLength, max_words=wordLength)
    else:
        generatedText = generator.gen_sentence(min_words=(wordLength), max_words=wordLength)
    generatedTextList = generatedText.split(' ')
    for word in words:
        if isinstance(word, list):
            wordIndex = words.index(word)
            try:
                generatedTextList[wordIndex] = '\n'.join([generatedTextList[wordIndex], generatedTextList[wordIndex + 1]])
                generatedTextList.pop(wordIndex + 1)
            except:
                try:
                    generatedTextList[wordIndex] = f'{str(generatedTextList[wordIndex])}\n'
                except:
                    errorData = f'dataIn: {dataIn};\nwords: {words};\n\n'
                    print(f'{colorama.Fore.RED}{errorData}{colorama.Style.RESET_ALL}')
                    with open('./log.txt', 'at') as writeError:
                        writeError.write(errorData)
                    if len(generatedTextList) < 1:
                        generatedTextList.append('\n')
        else:
            continue
    dataOut = ' '.join(generatedTextList)
    return(dataOut)

def rnnRandomSentence(dataIn: str, temperature):
    words = dataIn.split(' ')
    # Filters out NewLine chars
    for word in words:
        if '\n' in word:
            words[words.index(word)] = word.split('\n')

    def getTrueLength(listIn: list) -> int:
        trueCount = 0
        for word in listIn:
            if isinstance(word, str):
                trueCount += 1
            elif isinstance(word, list):
                trueCount += getTrueLength(word)
            else:
                print("Wasn't a string or list")
                continue
        return trueCount

    wordLength = getTrueLength(words)
    rnnGenerator.config['max_length'] = wordLength
    if temperature == 'random':
        temperature = round(random.uniform(0.0, 1.0), 4)
    generatedText = rnnGenerator.generate(n=1, temperature=temperature)
    generatedTextList = generatedText.split(' ')
    for word in words:
        if isinstance(word, list):
            wordIndex = words.index(word)
            try:
                generatedTextList[wordIndex] = '\n'.join([generatedTextList[wordIndex], generatedTextList[wordIndex + 1]])
                generatedTextList.pop(wordIndex + 1)
            except:
                try:
                    generatedTextList[wordIndex] = f'{str(generatedTextList[wordIndex])}\n'
                except:
                    errorData = f'dataIn: {dataIn};\nwords: {words};\n\n'
                    print(f'{colorama.Fore.RED}{errorData}{colorama.Style.RESET_ALL}')
                    with open('./log.txt', 'at') as writeError:
                        writeError.write(errorData)
                    if len(generatedTextList) < 1:
                        generatedTextList.append('\n')
        else:
            continue
    dataOut = ' '.join(generatedTextList)
    return(dataOut)
