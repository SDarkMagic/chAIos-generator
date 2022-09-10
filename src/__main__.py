from distutils.text_file import TextFile
from os import read
import pathlib
import time
import argparse

#from tensorflow.python.keras.backend import rnn
import util
import bfres
import imgUtils as img
from essential_generators import MarkovTextGenerator, document_generator
from essential_generators import DocumentGenerator
#from textgenrnn import textgenrnn
import colorama
import random
import arrr
import json

colorama.init()

configPath = util.get_data_dir() / 'config.json'


parser = argparse.ArgumentParser(description='A tool for using AI text generation functions.')
subparsers = parser.add_subparsers()

# Ai Text Gen Method Subparser
useAiTextGen = subparsers.add_parser('Generate', aliases=['generate', 'gen'])
useAiTextGen.add_argument('-g', type=int, help='Game to be used; Input 0 for Botw, 1 for BDSP, or 2 for Splatoon 2. Defaults to 0', required=False, default=0, dest='game')
useAiTextGen.add_argument('-f', type=str, help="Path to the game's text file.", required=False, default=None, dest='textFile')
useAiTextGen.add_argument('-o', type=str, help='Path to output modified text files to.', required=False, default=None, dest='outputDir')
useAiTextGen.add_argument('-m', type=str, help='Name of the model to load for text generation (optional)', required=False, default='markov_textgen.json', dest='modelName')
useAiTextGen.add_argument('-t', '--temperature', help='A float value from 0 to 1 to be used as the generation temperature. (optional, defaults to 0.5', required=False,default=0.5, dest='temperature')

# Subparser for re-training the AI text gen model
retrain = subparsers.add_parser('Train', aliases=['train', 'retrain', 'Retrain'])
retrain.add_argument('-f', type=str, help='Path to text file containing data to retrain the model off of.', required=False, default=None, dest='trainingData')
retrain.add_argument('-o', type=str, help='Name to save the Generated model as (optional)', required=False, default='markov_textgen.json', dest='outputModelName')
retrain.add_argument('-n', type=int, help='Number of epochs to be used when training the new model. If the flag is not set, only one epoch will be run.', required=False, default=1, dest='epochs')

# Outputs a sample of what the AI can generate
sampleText = subparsers.add_parser('Sample', aliases=['sample'])
sampleText.add_argument('-m', type=str, help='Name of the model to load for text generation (optional)', required=False, default='markov_textgen.json', dest='modelName')
sampleText.add_argument('-t', '--temperature', help='A float value from 0 to 1 to be used as the generation temperature. (optional, defaults to 0.5', required=False,default=0.5, dest='temperature')

# pirate-ifies stuff
pirate = subparsers.add_parser('Pirate', aliases=['pirate'])
pirate.add_argument('-b', type=str, help='Path to the Bootup text file.', required=False, default=None, dest='bootupFile')
pirate.add_argument('-o', type=str, help='Path to output modified MSBT files to.', required=False, default=None, dest='outputDir')

# StockIco stuffs
stockIcoReplace = subparsers.add_parser('image')
stockIcoReplace.add_argument('-m', type=str, help='Name of the model to load for text generation (optional)', required=False, default='markov_textgen.json', dest='modelName')
stockIcoReplace.add_argument('-o', type=str, help='Location of the graphics pack to output the modified files to. IMPORTANT Replaces orignal files if none is specified. (optional)', required=False, default=None, dest='outputDir')

# Randomize both text and images
chaos = subparsers.add_parser('genChaos', aliases=['chaos', 'randomizeAll'])
chaos.add_argument('-m', type=str, help='Name of the model to load for text generation (optional)', required=False, default='markov_textgen.json', dest='modelName')
chaos.add_argument('-o', type=str, help='Location of the graphics pack to output the modified files to. IMPORTANT Replaces orignal files if none is specified. (optional)', required=False, default=None, dest='outputDir')

generator = DocumentGenerator()
#rnnGenerator = textgenrnn()

def checkType(valIn, typeCheck):
    if isinstance(valIn, typeCheck):
        return (True, valIn)
    else:
        try:
            newVal = typeCheck(valIn)
            return(newVal)
        except:
            print(f'Value: {valIn} either could not be converted to, or was not type {typeCheck}. Please try the command again with the correct data type.')
            return False

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

def AiGenText(args):
    global generator
    global rnnGenerator

    config = util.getConfigData()
    bootupPath = pathlib.Path(f"{config['gamePath']}/content/Pack/Bootup_USen.pack")
    if str(args.modelName).endswith('.json'):
        #args.modelName = f"{str(args.modelName).split('.')[0]}_weights.hdf5"
        pass
    else:
        #args.modelName = f"{str(args.modelName).split('.')[0]}_weights.hdf5"
        args.modelName = args.modelName + '.json'

    if checkType(args.temperature, float) != False:
        temperature = args.temperature
    else:
        if args.temperature == 'random':
            temperature = 'random'
        else:
            return

    #rnnGenerator.load(f"{util.get_data_dir()}/Models/RNN/{args.modelName}")
    generator.text_generator = MarkovTextGenerator(model=f'{util.get_data_dir()}/Models/{args.modelName}')

    if args.outputDir == None:
        outputDir = input('Path to the graphic pack directory where the file(s) will be outputted ')
    else:
        outputDir = args.outputDir

    if args.game == 0:
        if args.textFile == None:
            bootupPath = pathlib.Path(f'{util.getConfigData()["gamePath"]}/content/Pack/Bootup_USen.pack')
        else:
            bootupPath = args.textFile

        bootup = util.Bootup_Msg(bootupPath)
        for directory in bootup.textFiles.keys():
            for file in bootup.textFiles[directory].keys():
                filePath = f'Message/Msg_{bootup.region}{bootup.language}.product.ssarc//{directory}/{file}'
                newMsbtData = bootup.replaceFileData(filePath, randomSentence, temperature=temperature)
                outFilePath = pathlib.Path(util.findMKDir(f'{outputDir}/content/Pack/Bootup_{bootup.region}{bootup.language}/Message/Msg_{bootup.region}{bootup.language}.product//{directory}') / file).absolute()
                startTime = time.time()
                with open(outFilePath, 'wb') as writePath:
                    writePath.write(newMsbtData)
                    elapsedTime = time.time() - startTime
                    print(f'Wrote data to {outFilePath} in {elapsedTime} seconds.\n')
        print(bootup.getTotalElapsedTime())

    elif args.game == 1:
        if args.textFile == None:
            textPath = input('Path to the text file or text file directory to use as a base: ')
        else:
            textPath = args.textFile

        assets = util.UnityAsset(textPath)
        for file in assets.fileList:
            print(type(file))
            assets.openFile(str(file.absolute()))
            print(assets.env.file)
            assets.data = assets.readFileData(assets.env)
            outData, timeElapsed = assets.replaceFileData(randomSentence)
            print(f'Replaced data from the file "{file.name}" in {timeElapsed} seconds.')
            startTime = time.time()
            assets.saveData(assets.env, outData)
            savePath = pathlib.Path(f'{outputDir}/{file.name}-uncompressed')
            with open(savePath, 'wb') as saveFile:
                saveFile.write(assets.env.file.save(packer='none'))
                print(f'Wrote Data to {savePath.absolute()} in {time.time() - startTime} seconds.\n')
        print(assets.getTotalElapsedTime())

    elif args.game == 2:
        print('Currently unsupported game. Exiting...')
        return

    else:
        print("Invalid game selection; terminating...")
        return

def randomStockIco(args):
    global generator
    def getImages(totalImageCount, imgDir: pathlib.Path):
        queries = []
        imageCount = totalImageCount - len(list(imgDir.iterdir()))
        i = 0
        while i <= imageCount:
            query = generator.gen_sentence(min_words=1, max_words=random.randint(1, 6))
            queries.append(query)
            i += 1
        img.findImages(queries, fileTypes='png', saveDir=str(imgDir.absolute()))
        input(f'Please review all images in the directory: "{str(imgDir.absolute())}" before continuing. If all images are appropriate for the intended audience, press any key to continue. Otherwise, simply delete the files from the directory that are problematic and images will be re-fetched to replace them.')
        currentImgs = list(imgDir.iterdir())
        print(currentImgs)
        currentImgCount = len(list(imgDir.iterdir()))
        if currentImgCount < totalImageCount:
            getImages(totalImageCount, imgDir)

        print('Finished fetching images.')
        return imgDir

    if str(args.modelName).endswith('.json'):
        pass
    else:
        args.modelName = args.modelName + '.json'

    generator.text_generator = MarkovTextGenerator(model=f'{util.get_data_dir()}/Models/{args.modelName}')

    config = util.getConfigData()
    icoPath = pathlib.Path(f"{config['gamePath']}/content/UI/StockItem")
    iconFiles = list(icoPath.iterdir())
    imgDir = util.findMKDir('./downloadedImages')
    icoNum = len(iconFiles)
    downloadedImgs = getImages(icoNum, imgDir)
    completed_images = []
    for image in util.findMKDir(args.outputDir).iterdir():
        completed_images.append(image.name)
    for file in iconFiles:
        selectedImg = random.choice(list(downloadedImgs.iterdir()))
        bfres.replaceBfresImg(file, selectedImg, util.findMKDir(args.outputDir), completed_images)
    print('Finished replacing all Icons')
    return


def sample(args):
    global generator
    global rnnGenerator
    args.modelName = f"{str(args.modelName).split('.')[0]}.json"
    #args.modelName = f"{str(args.modelName).split('.')[0]}_weights.hdf5"
    #rnnGenerator.load(f"{util.get_data_dir()}/Models/RNN/{args.modelName}")
    #if checkType(args.temperature, float) != False:
     #   temperature = args.temperature

    generator.text_generator = MarkovTextGenerator(model=f'{util.get_data_dir()}/Models/{args.modelName}')
    generator.init_sentence_cache()
   # sentence_cache = rnnGenerator.generate(1000, return_as_list=True, temperature=temperature)
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
    if not str(args.outputModelName).endswith('.json'):
        args.outputModelName = f'{args.outputModelName}.json'
    with open(trainingDataFile, 'rt', encoding='utf-8') as readData:
        trainingData = readData.readlines()

    # Deprecated method of training old models

    gen = MarkovTextGenerator(load_model=False)
    gen.train('\n'.join(util.clean_emotes(trainingData)))
    gen.save_model(f'{util.get_data_dir()}/Models/{args.outputModelName}')
    """
    gen=textgenrnn(name=f'{util.findMKDir(f"{util.get_data_dir()}/Models/RNN")}/{args.outputModelName}')
    gen.train_from_file(file_path=trainingDataFile, num_epochs=args.epochs)
    """
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

def randomizeAll(args):
    #AiGenText(args)
    randomStockIco(args)
    return

sampleText.set_defaults(func=sample)
useAiTextGen.set_defaults(func=AiGenText)
retrain.set_defaults(func=trainModel)
pirate.set_defaults(func=pirateMode)
stockIcoReplace.set_defaults(func=randomStockIco)
chaos.set_defaults(func=randomizeAll, temperature='random', game=0, textFile=None)

if __name__ == '__main__':
    args = parser.parse_args()
    args.func(args)
    colorama.deinit()