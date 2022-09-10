import UnityPy
import pathlib
import sys
import json
import util

"""
class UnityAsset:
    def __init__(self, dirIn):
        self.fileList = self.getFiles(dirIn)
        self.env = None


    def getFiles(self, dirIn):
        fileList = []
        if not isinstance(dirIn, pathlib.Path):
            dirIn = pathlib.Path(dirIn)

        if dirIn.is_dir():
            for subDir in dirIn.iterdir():
                fileList.extend(self.getFiles(subDir))
        else:
            fileList.append(dirIn)
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
                data = obj
            else:
                data = obj
            dataList.append(data)
        return

if __name__ == '__main__':
    dataList = []
    asset = UnityAsset(sys.argv[1])
    asset.openFile(str(asset.fileList[0].absolute()))
    data = json.dumps(dataList, indent=2)
    with open('./out.json', 'wt', encoding='utf8') as writeOut:
        writeOut.write(data)
    print(asset.env.objects)
"""


def testReplaceMethod(dataIn: str, **kwargs):
    return('a')


asset = util.UnityAsset(pathlib.Path("C:/Users/drago/Desktop/Pok__mon Shining Pearl v0 (010018E011D92000) (BASE)/Data/StreamingAssets/AssetAssistant/Message/common_msbt"))
asset.openFile(str(asset.fileList[0].absolute()))
print(asset.env.file)
asset.data = asset.readFileData(asset.env)

outdata, elapsedTime = asset.replaceFileData(testReplaceMethod)
asset.saveData(asset.env, outdata)
#print(outData)
with open('common', 'wb') as saveFile:
    saveFile.write(asset.env.file.save(packer='lz4'))

#with open('out.json', 'wt') as writeData:
#    outData = asset.replaceFileData(testReplaceMethod)
#    writeData.write(json.dumps(outData, indent=2))