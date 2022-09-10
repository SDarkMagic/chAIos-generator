# Handles searching for and downloading images from google's API
import json
import random
from apiclient.discovery import build
import urllib.request
import util

config = util.getConfigData()

service = build('customsearch', 'v1', developerKey=config['Google']['ApiKey'])

def findImage(query: str, fileType='png', num=10, saveDir='.'):
    res = service.cse().list(
        q=query,
        cx='01edab70514c54aca',
        searchType='image',
        num=num,
        fileType='png',
        safe='medium'
    ).execute()

    return res

def findImages(qList: list, fileTypes='png', saveDir='.'):
    for query in qList:
        try:
            imgResults = findImage(query, fileType=fileTypes, saveDir=saveDir)
            image = random.choice(imgResults['items'])
            urllib.request.urlretrieve(image['link'], f'{saveDir}/{util.cleanString(query)}.png')
        except Exception as e:
            print(e)
            continue

    return(saveDir)
