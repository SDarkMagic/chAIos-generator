import pathlib
import time
import argparse
import util
from essential_generators import MarkovTextGenerator, document_generator
from essential_generators import DocumentGenerator
from textgenrnn import textgenrnn
import colorama
import random
import arrr

colorama.init()




parser = argparse.ArgumentParser(description='A tool for using AI text generation functions.')
subparsers = parser.add_subparsers()

# Ai Text Gen Method Subparser
useAiTextGen = subparsers.add_parser('Generate', aliases=['generate', 'gen'])
useAiTextGen.add_argument('-b', type=str, help='Path to the Bootup text file.', required=False, default=None, dest='bootupFile')
useAiTextGen.add_argument('-o', type=str, help='Path to output modified MSBT files to.', required=False, default=None, dest='outputDir')
useAiTextGen.add_argument('-m', type=str, help='Name of the model to load for text generation (optional)', required=False, default='markov_textgen.json', dest='modelName')

# Subparser for re-training the AI text gen model
retrain = subparsers.add_parser('Train', aliases=['train', 'retrain', 'Retrain'])
retrain.add_argument('-f', type=str, help='Path to text file containing data to retrain the model off of.', required=False, default=None, dest='trainingData')
retrain.add_argument('-o', type=str, help='Name to save the Generated model as (optional)', required=False, default='markov_textgen.json', dest='outputModelName')
retrain.add_argument('-n', type=int, help='Number of epochs to be used when training the new model. If the flag is not set, only one epoch will be run.', required=False, default=1, dest='epochs')

# Outputs a sample of what the AI can generate
sampleText = subparsers.add_parser('Sample', aliases=['sample'])
sampleText.add_argument('-m', type=str, help='Name of the model to load for text generation (optional)', required=False, default='markov_textgen.json', dest='modelName')

# pirate-ifies stuff
pirate = subparsers.add_parser('Pirate', aliases=['pirate'])
pirate.add_argument('-b', type=str, help='Path to the Bootup text file.', required=False, default=None, dest='bootupFile')
pirate.add_argument('-o', type=str, help='Path to output modified MSBT files to.', required=False, default=None, dest='outputDir')


generator = DocumentGenerator()

def randomSentence(dataIn: str):
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

def AiGenText(args):
    global generator
    if args.bootupFile == None:
        bootupPath = input('Path to the Bootup text pack file to use as a base: ')
    else:
        bootupPath = args.bootupFile
    if args.outputDir == None:
        outputDir = input('Path to the directory where the files will be outputted(Please note that the directory structure MUST mimic the structure found within the Message.ssarc file) ')
    else:
        outputDir = args.outputDir
    if str(args.modelName).endswith('.json'):
        pass
    else:
        args.modelName = f'{args.modelName}.json'
    generator.text_generator = MarkovTextGenerator(model=f'{util.get_data_dir()}/Models/{args.modelName}')
    bootup = util.Bootup_Msg(bootupPath)
    for directory in bootup.textFiles.keys():
        for file in bootup.textFiles[directory].keys():
            filePath = f'Message/Msg_{bootup.region}{bootup.language}.product.ssarc//{directory}/{file}'
            newMsbtData = bootup.replaceFileData(filePath, randomSentence)
            outFilePath = pathlib.Path(f'{outputDir}/{directory}/{file}').absolute()
            with open(outFilePath, 'wb') as writePath:
                startTime = time.time()
                writePath.write(newMsbtData)
                elapsedTime = time.time() - startTime
                print(f'Wrote data to {outFilePath} in {elapsedTime} seconds.\n')
        print(bootup.getTotalElapsedTime())


def sample(args):
    global generator
    if str(args.modelName).endswith('.json'):
        pass
    else:
        args.modelName = f'{args.modelName}.json'
    generator.text_generator = MarkovTextGenerator(model=f'{util.get_data_dir()}/Models/{args.modelName}')
    generator.init_sentence_cache()
    with open('./sentenceCache.txt', 'wt', encoding='utf-8') as writeCache:
        cacheOut = str()
        for sentence in generator.sentence_cache:
            cacheOut = f'{cacheOut}\n{sentence}'
        writeCache.write(cacheOut)

def trainModel(args):
    if args.trainingData == None:
        trainingDataFile = input('Path to the text file to be used to train the AI model: ')
    else:
        trainingDataFile = args.trainingData
    if str(args.outputModelName).endswith('.json'):
        pass
    else:
        args.outputModelName = f'{args.outputModelName}.json'
    with open(trainingDataFile, 'rt', encoding='utf-8') as readData:
        trainingData = readData.read()

    # Deprecated method of training old models
    """
    gen = MarkovTextGenerator(load_model=False)
    gen.train(trainingData)
    gen.save_model(f'{util.get_data_dir()}/Models/{args.outputModelName}')
    """
    gen=textgenrnn()
    gen.train_from_file(file_path=trainingDataFile, num_epochs=args.epochs)
    print('Trained new model!')

def pirateMode(args):
    global generator
    if args.bootupFile == None:
        bootupPath = input('Path to the Bootup text pack file to use as a base: ')
    else:
        bootupPath = args.bootupFile
    if args.outputDir == None:
        outputDir = input('Path to the directory where the files will be outputted(Please note that the directory structure MUST mimic the structure found within the Message.ssarc file) ')
    else:
        outputDir = args.outputDir
    bootup = util.Bootup_Msg(bootupPath)
    for directory in bootup.textFiles.keys():
        for file in bootup.textFiles[directory].keys():
            filePath = f'Message/Msg_{bootup.region}{bootup.language}.product.ssarc//{directory}/{file}'
            newMsbtData = bootup.replaceFileData(filePath, arrr.translate)
            outFilePath = pathlib.Path(f'{outputDir}/{directory}/{file}').absolute()
            with open(outFilePath, 'wb') as writePath:
                startTime = time.time()
                writePath.write(newMsbtData)
                elapsedTime = time.time() - startTime
                print(f'Wrote data to {outFilePath} in {elapsedTime} seconds.\n')
        print(bootup.getTotalElapsedTime())

sampleText.set_defaults(func=sample)
useAiTextGen.set_defaults(func=AiGenText)
retrain.set_defaults(func=trainModel)
pirate.set_defaults(func=pirateMode)

if __name__ == '__main__':
    args = parser.parse_args()
    args.func(args)
    colorama.deinit()