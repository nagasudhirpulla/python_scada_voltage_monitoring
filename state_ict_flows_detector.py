import pandas as pd
from scada_fetcher import fetchScadaPntRealData


class StateIctFlowsDetector:
    masterFilePath = None
    ictsDf = None
    stateSuffixInfoDf = None

    def __init__(self, masterFilePath='secret/scada_points.xlsx', sheetName='transformers', stateTagsSheetName='state_tags'):
        self.masterFilePath = masterFilePath
        if masterFilePath not in [None, '']:
            # read bus voltages master data
            ictsDf = pd.read_excel(
                masterFilePath, sheetname=sheetName)
            ictsDf.point = ictsDf.service + ictsDf.point
            del ictsDf['service']
            self.ictsDf = ictsDf
            # read the state suffixes info to map with other sheets
            stateSuffixInfoDf = pd.read_excel(
                masterFilePath, sheetname=stateTagsSheetName)
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
            stateSuffixes)][['point', 'substation', 'dev_num', 'is_flipped']]
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
            return 'Number of ICTs = 0'
        # https://stackoverflow.com/questions/15705630/get-the-rows-which-have-the-max-value-in-groups-using-groupby
        ictStrings = stateIctsInfo.sort_values(by=['substation']).apply(
            lambda b: '{0} {1} ({2:.2f} MVAR)'.format(b.substation, b.dev_num, b['data']), axis=1).tolist()
        messageStr = 'Number of ICTs = {0}, '.format(len(ictStrings))
        messageStr += ', '.join(ictStrings)
        return messageStr
