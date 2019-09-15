import pandas as pd
from scada_fetcher import fetchScadaPntRealData

class StateLiveBrsDetector:
    masterFilePath = None
    brsDf = None
    stateSuffixInfoDf = None

    def __init__(self, masterFilePath='secret/scada_points.xlsx', sheetName='reactors', stateTagsSheetName='state_tags'):
        self.masterFilePath = masterFilePath
        if masterFilePath not in [None, '']:
            # read bus voltages master data
            brsDf = pd.read_excel(
                masterFilePath, sheet_name=sheetName)
            brsDf.point = brsDf.service + brsDf.point
            del brsDf['service']
            self.brsDf = brsDf
            # read the state suffixes info to map with other sheets
            stateSuffixInfoDf = pd.read_excel(
                masterFilePath, sheet_name=stateTagsSheetName)
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
            stateSuffixes)][['point', 'substation', 'dev_num']]
        # find the bus voltage of each bus
        stateBrsDf['data'] = stateBrsDf.point.apply(
            lambda x: fetchScadaPntRealData(x))
        # find if the bus voltages are high above limits
        stateBrsDf['is_br_on'] = stateBrsDf.apply(lambda x: True if (
            abs(x['data']) > 5) else False, axis=1)
        brsInfo = stateBrsDf[stateBrsDf.is_br_on == isOn]
        return brsInfo
