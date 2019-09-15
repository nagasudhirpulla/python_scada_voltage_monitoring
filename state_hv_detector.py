import pandas as pd
from scada_fetcher import fetchScadaPntRealData

class StateHvDetector:
    voltViolLims = {765: {'high': 800, 'low': 740},
                    400: {'high': 420, 'low': 380},
                    220: {'high': 240, 'low': 200}}
    masterFilePath = None
    busVoltsDf = None
    stateSuffixInfoDf = None

    def __init__(self, masterFilePath='secret/scada_points.xlsx', sheetName='bus_voltages', stateTagsSheetName='state_tags'):
        self.masterFilePath = masterFilePath
        if masterFilePath not in [None, '']:
            # read bus voltages master data
            busVoltsDf = pd.read_excel(
                masterFilePath, sheet_name=sheetName)
            busVoltsDf.point = busVoltsDf.service + busVoltsDf.point
            del busVoltsDf['service']
            self.busVoltsDf = busVoltsDf
            # read the state suffixes info to map with other sheets
            stateSuffixInfoDf = pd.read_excel(
                masterFilePath, sheet_name=stateTagsSheetName)
            self.stateSuffixInfoDf = stateSuffixInfoDf

    # returns indices of buses which have high voltage
    def getHvBusesInfoForState(self, state):
        # get voltage limits
        voltViolLims = self.voltViolLims
        # get bus voltage master data table
        busVoltsDf = self.busVoltsDf
        # get the tags for the state
        stateSuffixInfoDf = self.stateSuffixInfoDf
        stateSuffixes = stateSuffixInfoDf[stateSuffixInfoDf.State == state].Tag.tolist(
        )
        # get all the buses corresponding to the state
        stateBusesDf = busVoltsDf[busVoltsDf.ss_suffix.isin(
            stateSuffixes)][['point', 'substation', 'dev_num']]
        # find the bus voltage of each bus
        stateBusesDf['base_voltage'] = stateBusesDf.dev_num.apply(lambda x: 400 if x.startswith(
            '4') else 765 if x.startswith('7') else 220 if x.startswith('2') else 0)
        stateBusesDf['data'] = stateBusesDf.point.apply(
            lambda x: fetchScadaPntRealData(x))
        # find if the bus voltages are high above limits
        stateBusesDf['is_high_volt'] = stateBusesDf.apply(lambda x: True if (
            abs(x['data']) > voltViolLims[x.base_voltage]['high']) else False, axis=1)
        hvBusesInfo = stateBusesDf[stateBusesDf.is_high_volt ==
                                   True]
        return hvBusesInfo
