import pandas as pd
from scada_fetcher import fetchScadaPntRealData
from appConfig import stateNames
from texttable import Texttable


class StateGtFlowsDetector:
    masterFilePath = None
    gtsDf = None
    stateSuffixInfoDf = None

    def __init__(self, masterFilePath='secret/scada_points.xlsx', sheetName='transformers', stateTagsSheetName='state_tags'):
        self.masterFilePath = masterFilePath
        if masterFilePath not in [None, '']:
            # read bus voltages master data
            gtsDf = pd.read_excel(
                masterFilePath, sheetName)
            gtsDf.point = gtsDf.service + gtsDf.point
            del gtsDf['service']
            self.gtsDf = gtsDf
            # read the state suffixes info to map with other sheets
            stateSuffixInfoDf = pd.read_excel(
                masterFilePath, stateTagsSheetName)
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
            stateSuffixes)][['point', 'substation', 'station_name', 'dev_num', 'is_flipped']]
        if stateGtsDf.shape[0] == 0:
            return stateGtsDf
        # find the bus voltage of each bus
        stateGtsDf['data'] = stateGtsDf.apply(
            lambda x: fetchScadaPntRealData(x.point)*(1 if x.is_flipped == 0 else -1), axis=1)
        # find if the bus voltages are high above limits
        stateGtsDf['is_flow_reverse'] = stateGtsDf.apply(lambda x: True if (
            x['data'] < -1) else False, axis=1)
        gtsInfo = stateGtsDf[stateGtsDf.is_flow_reverse == isFlowReverse]
        gtsInfo = gtsInfo[gtsInfo['data'].abs() > 1]
        return gtsInfo

    def generateMessage(self, state, isFlowReverse=True):
        stateGtsInfo = self.getGtsInfoForState(state, isFlowReverse)
        if stateGtsInfo.shape[0] == 0:
            return ''
        # https://stackoverflow.com/questions/15705630/get-the-rows-which-have-the-max-value-in-groups-using-groupby
        gtRows = stateGtsInfo.sort_values(by=['station_name']).apply(
            lambda b: [b.station_name, b.dev_num, '{0:.2f}'.format(b['data'])], axis=1).tolist()
        messageStr = 'The following GTs are not absorbing MVAR in {0} substations: \n'.format(
            stateNames[state])
        messageStr += 'Number of GTs = {0}\n'.format(len(gtRows))
        messageStr += '\n'
        table = Texttable()
        table.set_deco(Texttable.HEADER | Texttable.BORDER | Texttable.VLINES)
        table.set_cols_dtype(['t', 't', 't'])
        table.set_cols_align(["l", "l", "l"])
        gtRows.insert(0, ["Substation", "Device Name", "MVAR"])
        table.add_rows(gtRows)
        messageStr += table.draw()
        return messageStr
