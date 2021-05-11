import random
import requests
from appConfig import getAppConfig


def fetchScadaPntRealData(pntId):
    urlStr = getAppConfig()["rtDataUrlBase"]
    paramsObj = {'pnt': pntId}
    r = requests.get(url=urlStr, params=paramsObj)
    data = r.json()
    return data['dval']


def fetchScadaPntRandData(pntId):
    return random.randint(-50, 50)


def fetchScadaPntRealData1(pntId):
    return random.randint(-50, 50)
