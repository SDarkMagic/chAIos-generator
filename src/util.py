# Miscellanious utility functions
import oead
import pathlib
from platform import system
import os
from wildbits._sarc import *
from pymsyt import Msbt
import time
import UnityPy
import json
import string

# Checks if a directory exists and makes it if not
def findMKDir(checkDir):
    if isinstance(checkDir, pathlib.Path):
        checkDir = checkDir
    else:
        try:
            checkDir = pathlib.Path(checkDir)
        except:
            print('Failed to make the pathlib instance :(')
            return
    if checkDir.exists():
        return checkDir
    else:
        if ("." in pathlib.PurePath(checkDir).name):
            checkFile = checkDir
            checkDir = checkDir.parents[0]
            checkDir.mkdir(parents=True, exist_ok=True)
            checkFile.touch()
            return checkFile
        checkDir.mkdir(parents=True, exist_ok=True)
        return checkDir

def get_data_dir() -> Path:
    if system() == "Windows":
        data_dir = pathlib.Path(os.path.expandvars("%LOCALAPPDATA%")) / "AiTextGen"
    else:
        data_dir = pathlib.Path.home() / ".config" / "AiTextGen"
    if not data_dir.exists():
        data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

def getConfigData():
    dataDir = get_data_dir()
    configPath = dataDir / 'config.json'
    with open(configPath, 'rt') as readConfig:
        config = json.loads(readConfig.read())
    return config

def cleanString(stringIn: str):
    punctuation = string.punctuation
    transTable = str.maketrans('', '', punctuation)
    return stringIn.translate(transTable)

def clean_emotes(lines: list):
    linesOut = []
    prefixes = getConfigData()['emotePrefixes']
    for line in lines:
        newLine = []
        for word in line.split(' '):
            for prefix in prefixes:
                if not word.startswith(prefix) and word.encode(encoding='UTF-16', errors='ignore').decode(encoding='UTF-16') != '':
                    newLine.append(word)
                else:
                    continue
        if len(newLine) > 0:
            linesOut.append(' '.join(newLine))
        else:
            continue
    return linesOut

class Bootup_Msg:
    def __init__(self, bootupPath):
        self.bootupPath = pathlib.Path(bootupPath)
        self.region = self.bootupPath.name.rstrip('.pack').split('_')[1][:2]
        self.language = self.bootupPath.name.rstrip('.pack').split('_')[1][2:]
        self.sarc, self.sarcTree, self.moddedFiles = open_sarc(self.bootupPath)
        self.textFiles =  self.sarcTree['Message'][f'Msg_{self.region}{self.language}.product.ssarc']
        self.startTime = time.time()

    def replaceFileData(self, fileName, replacementMethod, **kwargs):
        startTime = time.time()
        fileData = get_nested_file_data(self.sarc, fileName)
        big_endian = fileData[0x08:0x0A] == b"\xfe\xff"
        #print(fileName, big_endian)
        msbtBinData = Msbt.from_binary(fileData)
        msbtData = msbtBinData.to_dict()
        #print(msbtData)
        entries = msbtData['entries']
        outputEntries = {}
        for entry in entries.keys():
            entryData = entries[entry]
            #print(entry)
            entryContents = entryData['contents']
            for subEntry in entryContents:
                if isinstance(subEntry, dict):
                    if 'text' in subEntry.keys():
                        entryIdx = entryContents.index(subEntry)
                        entryContents[entryIdx] = {'text': replacementMethod(subEntry['text'], **kwargs)}
                    else:
                        continue
                else:
                    continue
            #entryData['contents'] = entryContents
            outputEntries.update({entry: entryData})
        #print(outputEntries)
        msbtData['entries'] = outputEntries
        #print(msbtData)
        functionTime = time.time() - startTime
        print(str(f'Function completed in {functionTime} seconds.'))
        return Msbt.from_dict(msbtData).to_binary(big_endian=big_endian)

    # Writes binary data to a file in a sarc based off of the path passed through 'file'
    def updateSarcData(self, filePath, data: bytes):
        startTime = time.time()
        replace_file(self.sarc, filePath, data)
        finishTime = time.time() - startTime
        print(f'Updated data contained in {filePath} in {finishTime} seconds.')

    def saveSarc(self):
        data = oead.SarcWriter.from_sarc(self.sarc).write()[1]
        self.bootupPath.write_bytes(data)

    def getTotalElapsedTime(self):
        elapsedTime = time.time() - self.startTime
        return str(f'Total Elapsed Time: {elapsedTime} seconds')

class UnityAsset:
    def __init__(self, dirIn):
        self.startTime = time.time()
        self.fileList = self.getFiles(dirIn)
        self.env = None
        self.data = None


    def getFiles(self, dirIn):
        fileList = []
        if not isinstance(dirIn, pathlib.Path):
            dirIn = pathlib.Path(dirIn)

        if dirIn.is_dir():
            for subDir in dirIn.iterdir():
                fileList.extend(self.getFiles(subDir))
        elif dirIn.is_file():
            fileList.append(dirIn)
        else:
            print('Inputted path was not a File or Directory')
            return
        return fileList

    def openFile(self, file):
        if self.env == None:
            self.env = UnityPy.load(file)
        else:
            self.env.load(file)
        return

    def readFileData(self, asset: UnityPy.Environment):
        dataList = []
        for obj in asset.objects:
            if obj.type.name == 'MonoBehaviour':
                if obj.serialized_type.nodes:
                    data = obj.read_typetree()
                else:
                    data = obj.read()
            elif obj.type.name == 'TextAsset':
                data = obj.read()
            else:
                data = obj.read()
            dataList.append(data)
        return dataList

    def saveData(self, asset: UnityPy.Environment, dataList: list):
        for obj in asset.objects:
            if obj.serialized_type.nodes:
                try:
                    obj.save_typetree(dataList[int(asset.objects.index(obj))])
                except:
                    continue
            else:
                continue
        return

    def replaceFileData(self, replacementMethod, **kwargs):
        startTime = time.time()
        fileData = self.data

        outputEntries = {}
        for entry in fileData:
            entryIdx = fileData.index(entry)
            entryData = fileData[entryIdx]
            try:
                labelDataArray = entryData['labelDataArray']
                labelDataOut = []
                for labelData in labelDataArray:
                    wordDataArray = labelData['wordDataArray']
                    for wordData in wordDataArray:
                        string = wordData['str']
                        try:
                            wordData['str'] = replacementMethod(string, **kwargs)
                        except:
                            print('Failed to update String value')
                            continue
                    labelData['WordDataArray'] = wordDataArray
                    labelDataOut.append(labelData)
                #print(labelDataOut)
                entryData['labelDataArray'] = labelDataOut
                fileData[entryIdx] = entryData
            except:
                print('Exception Occured in ReplaceFileData')
                continue
        elapsedTime = time.time() - startTime
        return fileData, elapsedTime

    def getTotalElapsedTime(self):
        return(str(f'Total elapsed time: {time.time() - self.startTime} seconds.'))

        """
        #print(outputEntries)
        msbtData['entries'] = outputEntries
        #print(msbtData)
        functionTime = time.time() - startTime
        print(str(f'Function completed in {functionTime} seconds.'))
        return Msbt.from_dict(msbtData).to_binary(big_endian=big_endian)
        """