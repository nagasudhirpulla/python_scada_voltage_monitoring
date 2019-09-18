import pandas as pd
from scada_fetcher import fetchScadaPntRealData


class StateGtFlowsDetector:
    masterFilePath = None
    gtsDf = None
    stateSuffixInfoDf = None

    def __init__(self, masterFilePath='secret/scada_points.xlsx', sheetName='transformers', stateTagsSheetName='state_tags'):
        self.masterFilePath = masterFilePath
        if masterFilePath not in [None, '']:
            # read bus voltages master data
            gtsDf = pd.read_excel(
                masterFilePath, sheetname=sheetName)
            gtsDf.point = gtsDf.service + gtsDf.point
            del gtsDf['service']
            self.gtsDf = gtsDf
            # read the state suffixes info to map with other sheets
            stateSuffixInfoDf = pd.read_excel(
                masterFilePath, sheetname=stateTagsSheetName)
            self.stateSuffixInfoDf = stateSuffixInfoDf

    # returns indices of buses which have high voltage
    def getGtsInfoForState(self, state, isFlowReverse=True):
        # get bus reactors master data table
        gtsDf = self.gtsDf
        # get the tags for the state
        stateSuffixInfoDf = self.stateSuffixInfoDf
        stateSuffixes = stateSuffixInfoDf[stateSuffixInfoDf.State == state].Tag.tolist(
        )
        # get all the brs corresponding to the state
        stateGtsDf = gtsDf[gtsDf.dev_num.apply(str).str.contains('g|u', case=False, regex=True) & gtsDf.ss_suffix.isin(
            stateSuffixes)][['point', 'substation', 'dev_num', 'is_flipped']]
        # find the bus voltage of each bus
        stateGtsDf['data'] = stateGtsDf.apply(
            lambda x: fetchScadaPntRealData(x.point)*(1 if x.is_flipped == 0 else -1), axis=1)
        # find if the bus voltages are high above limits
        stateGtsDf['is_flow_reverse'] = stateGtsDf.apply(lambda x: True if (
            x['data'] < -1) else False, axis=1)
        gtsInfo = stateGtsDf[stateGtsDf.is_flow_reverse == isFlowReverse]
        return gtsInfo
    
    def generateMessage(self, state, isFlowReverse=True):
        stateGtsInfo = self.getGtsInfoForState(state, isFlowReverse)
        if stateGtsInfo.shape[0] == 0:
            return 'Number of GTs = 0'
        # https://stackoverflow.com/questions/15705630/get-the-rows-which-have-the-max-value-in-groups-using-groupby
        gtStrings = stateGtsInfo.sort_values(by=['substation']).apply(lambda b: '{0} {1} ({2:.2f} MVAR)'.format(b.substation, b.dev_num, b['data']), axis=1).tolist()
        messageStr = 'Number of GTs = {0}, '.format(len(gtStrings))
        messageStr += ', '.join(gtStrings)
        return messageStr
