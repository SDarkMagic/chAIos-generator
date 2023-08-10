# Handles any functions related to directly reading and writing both bfres and texture data
from io import BytesIO
import clr
import sys
import oead
import pathlib
from PIL import Image
import json
import util

bfresLibPath = pathlib.Path(__file__).parent / 'lib\\BfresLibrary\\BfresLibrary\\bin\\Debug\\net45'
sys.path.append(bfresLibPath)

clr.AddReference('BfresLibrary')
clr.AddReference("System.IO")
from BfresLibrary import ResFile
from BfresLibrary.Swizzling import GX2
from BfresLibrary.GX2 import GX2CompSel
from System.IO import MemoryStream, SeekOrigin

def decompressBfres(bfresPath):
    with open(bfresPath, 'rb') as readData:
        decompressedData = oead.yaz0.decompress(readData.read())
    #with open(bfresPath, 'wb') as writeData:
        #writeData.write(decompressedData)
    return decompressedData

def compressBfres(bfresPath):
    with open(bfresPath, 'rb') as readData:
        compressedData = oead.yaz0.compress(readData.read())
    with open(bfresPath, 'wb') as writeData:
        writeData.write(compressedData)
    return

#print('imported BfresLibrary texture support successfully')

def replaceBfresImg(bfresPath, imgPath, outPath=None, completed_images=[]):
    if not isinstance(bfresPath, pathlib.Path):
        bfresPath = pathlib.Path(bfresPath)

    if not isinstance(imgPath, pathlib.Path):
        imgPath = pathlib.Path(imgPath)

    if bfresPath.name in completed_images:
        return

    try:
        decompBfres = bytearray(decompressBfres(bfresPath))
    except:
        print('failed to decompress file')
        with open(bfresPath, 'rb') as readBfres:
            decompBfres = bytearray(readBfres.read())

    bfresStream = MemoryStream()
    bfresStream.Write(decompBfres, 0, len(decompBfres))
    bfresStream.Seek(0, SeekOrigin.Begin)

    file = ResFile(bfresStream)
    texture = file.Textures[0].Value
    print(f'fileName: {texture.Name}')

    # Swizzling stuffs I think
    #with open(pathlib.Path(str(imgPath.absolute())), 'rb') as readBin:
    imgdata = Image.open(str(imgPath.absolute()))

    if len(imgdata.split()) <= 3:
        imgdata = imgdata.convert('RGBA')

    if len(imgdata.split()) < 4:
        print('Added alpha channel')
        imgdata.putalpha(0)

    # swap r and b channels because botw is silly
    try:
        r, g ,b, a = imgdata.split()
        imgdata = Image.merge('RGBA', (b, g, r, a))
    except Exception as e:
        print(f'Error occurred trying to process {imgPath.name} -- {e}')

    # Convert the png to a dds
    temp = BytesIO() #Creates a temporary in memory storage area for the image data to save to
    imgdata.save(temp, format='dds')
    ddsImg = temp.getvalue()

    # Actual texture data creation and updating details to match in the resfile texture object
    gx2Texture = GX2.CreateGx2Texture(ddsImg, texture.Name, texture.TileMode, texture.AAMode, imgdata.width, imgdata.height, texture.Depth, texture.Format, texture.SwizzlePattern, texture.Dim, texture.MipCount)
    print('Successfully created gx2Texture')

    texture.set_Data(gx2Texture.data)
    texture.set_Width(imgdata.width)
    texture.set_Height(imgdata.height)

    # Swap the Red and Blue channels in the FTEX file because converting to a DDS causes them to swap for some reason
    #texture.set_CompSelR(GX2CompSel.ChannelB)
    #texture.set_CompSelB(GX2CompSel.ChannelR)

    #texValue = texture.get_Data() # This line is just for debugging and checking the actual data for the texture that was replaced
    if outPath != None:
        bfresPath = util.findMKDir(f'{outPath}/content/UI/StockItem') / bfresPath.name
    file.Save(str(bfresPath.absolute()))
    #bfresStream.Dispose()
    try:
        compressBfres(bfresPath)
    except:
        print('failed to recompress file')

if __name__ == '__main__':
    replaceBfresImg("C:/Users/drago/Desktop/Relics-Of-The-Past-ORG-Main/Src/content/Model/Enemy_Lynel_Gold_Ancient.sbfres", "C:/Users/drago/Desktop/BotW_MassTextChanges/assets/Kirby.png")