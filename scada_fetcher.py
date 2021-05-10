'''
Using Popen to communicate with exe file
https://docs.python.org/3.4/library/subprocess.html#subprocess.Popen.communicate
use shlex to parse command string if required
shlex.split(/bin/vikings -input eggs.txt -output "spam spam.txt" -cmd "echo '$MONEY'")
will give
['/bin/vikings', '-input', 'eggs.txt', '-output', 'spam spam.txt', '-cmd', "echo '$MONEY'"]
'''
import random
import requests
from subprocess import Popen, PIPE, TimeoutExpired
import datetime as dt
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


def fetchScadaPntRealExeData(pntId):
    command = "./ScadaCsharpNodeAdapter.exe"
    proc = Popen([command, "--request_type", "real",
                  "--meas_id", pntId], stdout=PIPE)
    try:
        outs, errs = proc.communicate(timeout=15)
    except TimeoutExpired:
        proc.kill()
    resp = outs.decode("utf-8")
    # split the response by comma
    respSegs = resp.split(',')
    if len(respSegs) < 2:
        return None
    else:
        return float(respSegs[0])


def convertEpochMsToDt(epochMs):
    timeObj = dt.datetime.fromtimestamp(epochMs/1000)
    return timeObj
