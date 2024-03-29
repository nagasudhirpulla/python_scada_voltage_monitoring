import pandas as pd
from scada_fetcher import fetchScadaPntRealData
from appConfig import stateNames
from texttable import Texttable


class StateLiveBrsDetector:
    masterFilePath = None
    brsDf = None
    stateSuffixInfoDf = None

    def __init__(self, masterFilePath='secret/scada_points.xlsx', sheetName='reactors', stateTagsSheetName='state_tags'):
        self.masterFilePath = masterFilePath
        if masterFilePath not in [None, '']:
            # read bus voltages master data
            brsDf = pd.read_excel(
                masterFilePath, sheetName)
            brsDf.point = brsDf.service + brsDf.point
            del brsDf['service']
            self.brsDf = brsDf
            # read the state suffixes info to map with other sheets
            stateSuffixInfoDf = pd.read_excel(
                masterFilePath, stateTagsSheetName)
            self.stateSuffixInfoDf = stateSuffixInfoDf

    # returns indices of buses which have high voltage
    def getBrsInfoForState(self, state, isOn=True):
        # get bus reactors master data table
        brsDf = self.brsDf
        # get the tags for the state
        stateSuffixInfoDf = self.stateSuffixInfoDf
        stateSuffixes = stateSuffixInfoDf[stateSuffixInfoDf.State == state].Tag.tolist(
        )
        # get all the brs corresponding to the state
        stateBrsDf = brsDf[~brsDf.dev_num.apply(str).str.endswith('LR') & brsDf.ss_suffix.isin(
            stateSuffixes)][['point', 'substation', 'station_name', 'dev_num', 'is_flipped']]
        if stateBrsDf.shape[0] == 0:
            return stateBrsDf
        # find the bus voltage of each bus
        stateBrsDf['data'] = stateBrsDf.apply(
            lambda x: fetchScadaPntRealData(x.point)*(1 if x.is_flipped == 0 else -1), axis=1)
        # find if the bus voltages are high above limits
        stateBrsDf['is_br_on'] = stateBrsDf.apply(lambda x: True if (
            abs(x['data']) > 5) else False, axis=1)
        brsInfo = stateBrsDf[stateBrsDf.is_br_on == isOn]
        return brsInfo

    def generateMessage(self, state, isOn=True):
        stateOffBrsInfo = self.getBrsInfoForState(state, isOn)
        if stateOffBrsInfo.shape[0] == 0:
            return ''
        # https://stackoverflow.com/questions/15705630/get-the-rows-which-have-the-max-value-in-groups-using-groupby
        brRows = stateOffBrsInfo.sort_values(by=['station_name']).apply(
            lambda b: [b.station_name, b.dev_num], axis=1).tolist()
        switchStateStr = "in service" if isOn else "out"
        messageStr = 'The following Bus reactors are {0} in {1} substations: \n'.format(
            switchStateStr, stateNames[state])
        messageStr += 'Number of Bus Reactors {0} = {1}\n'.format(
            switchStateStr, len(brRows))
        messageStr += '\n'
        table = Texttable()
        table.set_deco(Texttable.HEADER | Texttable.BORDER | Texttable.VLINES)
        table.set_cols_dtype(['t', 't'])
        table.set_cols_align(["l", "l"])
        brRows.insert(0, ["Substation", "Device Name"])
        table.add_rows(brRows)
        messageStr += table.draw()
        return messageStr
