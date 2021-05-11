import pandas as pd
from scada_fetcher import fetchScadaPntRealData
from appConfig import stateNames
from texttable import Texttable


class StateIctFlowsDetector:
    masterFilePath = None
    ictsDf = None
    stateSuffixInfoDf = None

    def __init__(self, masterFilePath='secret/scada_points.xlsx', sheetName='transformers', stateTagsSheetName='state_tags'):
        self.masterFilePath = masterFilePath
        if masterFilePath not in [None, '']:
            # read bus voltages master data
            ictsDf = pd.read_excel(
                masterFilePath, sheetName)
            ictsDf.point = ictsDf.service + ictsDf.point
            del ictsDf['service']
            self.ictsDf = ictsDf
            # read the state suffixes info to map with other sheets
            stateSuffixInfoDf = pd.read_excel(
                masterFilePath, stateTagsSheetName)
            self.stateSuffixInfoDf = stateSuffixInfoDf

    # returns indices of buses which have high voltage
    def getIctsInfoForState(self, state, isFlowReverse=True):
        # get bus reactors master data table
        ictsDf = self.ictsDf
        # get the tags for the state
        stateSuffixInfoDf = self.stateSuffixInfoDf
        stateSuffixes = stateSuffixInfoDf[stateSuffixInfoDf.State == state].Tag.tolist(
        )
        # get all the brs corresponding to the state
        stateIctsDf = ictsDf[ictsDf.dev_num.apply(str).str.contains('t', case=False, regex=True) & ictsDf.ss_suffix.isin(
            stateSuffixes)][['point', 'substation', 'station_name', 'dev_num', 'is_flipped']]
        if stateIctsDf.shape[0] == 0:
            return stateIctsDf
        # find the bus voltage of each bus
        stateIctsDf['data'] = stateIctsDf.apply(
            lambda x: fetchScadaPntRealData(x.point)*(1 if x.is_flipped == 0 else -1), axis=1)
        # find if the bus voltages are high above limits
        stateIctsDf['is_flow_reverse'] = stateIctsDf.apply(lambda x: True if (
            x['data'] < -1) else False, axis=1)
        ictInfo = stateIctsDf[stateIctsDf.is_flow_reverse == isFlowReverse]
        ictInfo = ictInfo[ictInfo['data'].abs() > 1]
        return ictInfo

    def generateMessage(self, state, isFlowReverse=True):
        stateIctsInfo = self.getIctsInfoForState(state, isFlowReverse)
        if stateIctsInfo.shape[0] == 0:
            return ''
        # https://stackoverflow.com/questions/15705630/get-the-rows-which-have-the-max-value-in-groups-using-groupby
        ictRows = stateIctsInfo.sort_values(by=['station_name']).apply(
            lambda b: [b.station_name, b.dev_num, '{0:.2f}'.format(b['data'])], axis=1).tolist()
        messageStr = 'MVAR flow is from LV side to HV side in the following ICTs of {0} substations: \n'.format(
            stateNames[state])
        messageStr += 'Number of ICTs = {0}\n'.format(len(ictRows))
        messageStr += '\n'
        table = Texttable()
        table.set_deco(Texttable.HEADER | Texttable.BORDER | Texttable.VLINES)
        table.set_cols_dtype(['t', 't', 't'])
        table.set_cols_align(["l", "l", "l"])
        ictRows.insert(0, ["Substation", "Device Name", "MVAR"])
        table.add_rows(ictRows)
        messageStr += table.draw()
        return messageStr
