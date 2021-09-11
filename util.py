import oead
import pathlib
from platform import system
import os
from wildbits._sarc import *
from pymsyt import Msbt
import time

def get_data_dir() -> Path:
    if system() == "Windows":
        data_dir = pathlib.Path(os.path.expandvars("%LOCALAPPDATA%")) / "AiTextGen"
    else:
        data_dir = pathlib.Path.home() / ".config" / "AiTextGen"
    if not data_dir.exists():
        data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

class Bootup_Msg:
    def __init__(self, bootupPath):
        self.bootupPath = pathlib.Path(bootupPath)
        self.region = self.bootupPath.name.rstrip('.pack').split('_')[1][:2]
        self.language = self.bootupPath.name.rstrip('.pack').split('_')[1][2:]
        self.sarc, self.sarcTree, self.moddedFiles = open_sarc(self.bootupPath)
        self.textFiles =  self.sarcTree['Message'][f'Msg_{self.region}{self.language}.product.ssarc']
        self.startTime = time.time()

    def replaceFileData(self, fileName, replacementMethod):
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
                        entryContents[entryIdx] = {'text': replacementMethod(subEntry['text'])}
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