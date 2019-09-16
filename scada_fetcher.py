import random
import requests
def fetchScadaPntRealData(pntId):
    urlStr = "http://localhost:62448/api/values/real"
    paramsObj = {'pnt':pntId} 
    r = requests.get(url = urlStr, params = paramsObj)
    data = r.json()
    return data['dval']

def fetchScadaPntRandData(pntId):
    return random.randint(-50, 50)