import pandas as pd
from scada_fetcher import fetchScadaPntRealData
from appConfig import stateNames
from texttable import Texttable


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
                masterFilePath, sheetName)
            busVoltsDf.point = busVoltsDf.service + busVoltsDf.point
            del busVoltsDf['service']
            self.busVoltsDf = busVoltsDf
            # read the state suffixes info to map with other sheets
            stateSuffixInfoDf = pd.read_excel(
                masterFilePath, stateTagsSheetName)
            self.stateSuffixInfoDf = stateSuffixInfoDf

    # returns indices of buses which have high voltage
    def getHvBusesInfoForState(self, state, isForHigh=True):
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
            stateSuffixes)][['point', 'substation', 'station_name', 'dev_num', 'is_flipped']]
        if stateBusesDf.shape[0] == 0:
            return stateBusesDf
        # find the bus voltage of each bus
        stateBusesDf['base_voltage'] = stateBusesDf.dev_num.apply(lambda x: 400 if x.startswith(
            '4') else 765 if x.startswith('7') else 220 if x.startswith('2') else 0)
        stateBusesDf['data'] = stateBusesDf.apply(
            lambda x: fetchScadaPntRealData(x.point)*(1 if x.is_flipped == 0 else -1), axis=1)
        # find if the bus voltages are high above limits
        stateBusesDf['is_high_volt'] = stateBusesDf.apply(lambda x: True if (
            abs(x['data']) > voltViolLims[x.base_voltage]['high']) else False, axis=1)
        hvBusesInfo = stateBusesDf[stateBusesDf.is_high_volt ==
                                   isForHigh]
        return hvBusesInfo

    def generateMessage(self, state, isForHigh=True):
        stateHvBusInfo = self.getHvBusesInfoForState(state, isForHigh)
        if stateHvBusInfo.shape[0] == 0:
            return ''
        stateHvBusInfo['pu_val'] = stateHvBusInfo['data'] / \
            stateHvBusInfo['base_voltage']
        # https://stackoverflow.com/questions/15705630/get-the-rows-which-have-the-max-value-in-groups-using-groupby
        idx = stateHvBusInfo.groupby(['substation'])['pu_val'].transform(
            max) == stateHvBusInfo['pu_val']
        hvSsList = stateHvBusInfo[idx].sort_values(
            by=['pu_val'], ascending=False)
        ssRows = hvSsList.apply(
            lambda h: [h.station_name, '{0:.2f} kV'.format(h['data'])], axis=1).tolist()
        messageStr = "High voltages prevailed at the following {0} substations: \n".format(
            stateNames[state])
        messageStr += 'Number of High Voltage substations = {0}\n'.format(
            len(ssRows))
        messageStr += '\n'
        table = Texttable()
        table.set_deco(Texttable.HEADER | Texttable.BORDER | Texttable.VLINES)
        table.set_cols_dtype(['t', 't'])
        table.set_cols_align(["l", "l"])
        ssRows.insert(0, ["Substation", "Voltage"])
        table.add_rows(ssRows)
        messageStr += table.draw()
        return messageStr
