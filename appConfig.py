# import json module
import json

stateNames = {'gj': 'Gujarat', 'mh': 'Maharashtra',
              'mp': 'Madhya Pradesh', 'cg': 'Chhattisgarh', 'cs': 'Central Sector'}

# initialize the app config global variable
appConf = {}


def loadAppConfig(fName="secret/config.json"):
    # load config json into the global variable
    with open(fName) as f:
        global appConf
        appConf = json.load(f)
        return appConf


def getAppConfig():
    # get the cached application config object
    global appConf
    return appConf
