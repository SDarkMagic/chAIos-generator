# Contains all of the functions used to re-generate text data to help declutter the main script
import colorama
import random
import re
from essential_generators import DocumentGenerator
from googletrans import Translator, LANGUAGES
from google.cloud import translate_v2 as translate

colorama.init()

class Method:
    def __init__(self, func):
        self.method = func

    @staticmethod
    def get_true_length(list_in: list) -> int:
            true_count = 0
            for word in list_in:
                if isinstance(word, str):
                    true_count += len(word)
                elif isinstance(word, list):
                    true_count += Method.get_true_length(word)
                else:
                    print("Wasn't a string or list")
                    continue
            return true_count

    @staticmethod
    def flatten_string(data: str, return_indices=False):
        words = data.split(' ')
        indices = []
        for word in words:
            if '\n' in word:
                index = words.index(word)
                words[index] = word.split('\n')
                indices.append(index)
        return (words, indices) if return_indices == True else words

class Translate(Method):
    def __init__(self, obfuscation_depth=4) -> None:
        super().__init__(self.parse)
        self.lang_codes = list(LANGUAGES.keys())
        self.translator = translate.Client()
        self.language_order = self._gen_lang_order(obfuscation_depth)

    def _gen_lang_order(self, depth):
        langs = []
        i = 0
        while i < depth:
            current_lang = random.choice(self.lang_codes)
            if (len(langs) == 0 or langs[-1] != current_lang):
                langs.append(current_lang)
                i += 1
            else:
                continue
        langs.append('en')
        return langs

    def parse(self, data: str):
        words, new_line_positions = self.flatten_string(data, True)
        raw = data.replace('\n', ' ')
        current_string = raw
        result = ''

        for language in self.language_order:
            current_string = self.translator.translate(current_string, target_language=language)['translatedText']
        tmp = []
        i = 0
        tmp_string = current_string.split(' ')
        while i < len(tmp_string):
            word = tmp_string[i]
            if i in new_line_positions and i != len(tmp_string) - 1:
                word = '\n'.join([tmp_string[i], tmp_string[i + 1]])
                i += 2
            else:
                i += 1
            tmp.append(word)
        unicode_regex = re.compile(r'&#([0-9a-fA-F]*);')
        result = ' '.join(tmp) # Since the response from the translate API is html encoded, apostrophes must be decoded from their HTML entity counterpart
        unicode_chars = unicode_regex.search(result)
        if (unicode_chars != None):
            try:
                char = int(unicode_chars.groups()[0])
            except:
                char = int(f'0x{unicode_chars.groups()[0]}', base=16)
            converted_char = chr(char)
            result = unicode_regex.sub(converted_char, result)
        return result

class Markovian(Method):
    def __init__(self):
        self.generator = DocumentGenerator()
        super().__init__(self.random_sentence)

    def random_sentence(self, dataIn: str, **kwargs):
        words = self.flatten_string(dataIn)

        refresh_cache = random.randint(0, 10000)

        if refresh_cache == 3751:
            self.generator.init_sentence_cache()
            self.generator.init_word_cache()
        else:
            pass

        wordLength = self.get_true_length(words)
        if wordLength < 3:
            if wordLength == 1:
                generatedText = self.generator.text_generator.gen_word()
            else:
                generatedText = self.generator.gen_sentence(min_words=wordLength, max_words=wordLength)
        else:
            generatedText = self.generator.gen_sentence(min_words=(wordLength), max_words=wordLength)
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


"""
def rnnRandomSentence(dataIn: str, temperature):
    words = dataIn.split(' ')
    # Filters out NewLine chars
    for word in words:
        if '\n' in word:
            words[words.index(word)] = word.split('\n')

    wordLength = get_true_length(words)
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
"""

if __name__ == '__main__':
    t = Translate()
    print(t.parse("yeah, ai song covers and AI just saying stuff for a video I can't stand because it's just lazy. If the video is about someone making and using the AI to do the stuff, then I'm cool with it"))