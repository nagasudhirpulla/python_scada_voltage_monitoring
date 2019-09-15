from scada_fetcher import fetchScadaPntRealData
import pandas as pd
scadaMasterFilename = 'secret/scada_points.xlsx'

# read state suffix tags info from excel
stateSuffixInfoDf = pd.read_excel(scadaMasterFilename, sheet_name='state_tags')

# dump voltages data
busVoltsMasterDf = pd.read_excel(scadaMasterFilename, 'bus_voltages')
# for now only filter state elements
busVoltsMasterDf = busVoltsMasterDf[busVoltsMasterDf['ss_suffix'].isin(
    stateSuffixInfoDf.Tag.tolist())]
busVoltsMasterDf.point = busVoltsMasterDf.service + busVoltsMasterDf.point
del busVoltsMasterDf['service']
# get real time scada data for the points
busVoltsMasterDf['data'] = busVoltsMasterDf.point.apply(
    lambda x: fetchScadaPntRealData(x))
# dump the results
busVoltsMasterDf.to_excel('dumps/bus_volts_dump.xlsx', index=False)

# dump states bus reactors data
brMasterDf = pd.read_excel(scadaMasterFilename, 'reactors')
# for now only filter state elements which are bus reactors
brMasterDf = brMasterDf[~brMasterDf.dev_num.apply(str).str.endswith('LR') & brMasterDf['ss_suffix'].isin(
    stateSuffixInfoDf.Tag.tolist())]
brMasterDf.point = brMasterDf.service + brMasterDf.point
del brMasterDf['service']
# get real time scada data for the points
brMasterDf['data'] = brMasterDf.point.apply(
    lambda x: fetchScadaPntRealData(x))
# dump the results
brMasterDf.to_excel('dumps/br_dump.xlsx', index=False)

# dump states ICT data
ictMasterDf = pd.read_excel(scadaMasterFilename, 'transformers')
# for now only filter state elements which are ICTs
# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.str.contains.html
ictMasterDf = ictMasterDf[ictMasterDf.dev_num.apply(str).str.contains('t', case=False, regex=True) & ictMasterDf['ss_suffix'].isin(
    stateSuffixInfoDf.Tag.tolist())]
ictMasterDf.point = ictMasterDf.service + ictMasterDf.point
del ictMasterDf['service']
# get real time scada data for the points
ictMasterDf['data'] = ictMasterDf.point.apply(
    lambda x: fetchScadaPntRealData(x))
# dump the results
ictMasterDf.to_excel('dumps/ict_dump.xlsx', index=False)

# dump states GT data
gtMasterDf = pd.read_excel(scadaMasterFilename, 'transformers')
# for now only filter state elements which are GTs
gtMasterDf = gtMasterDf[gtMasterDf.dev_num.apply(str).str.contains('g|u', case=False, regex=True) & gtMasterDf['ss_suffix'].isin(
    stateSuffixInfoDf.Tag.tolist())]
gtMasterDf.point = gtMasterDf.service + gtMasterDf.point
del gtMasterDf['service']
# get real time scada data for the points
gtMasterDf['data'] = gtMasterDf.point.apply(
    lambda x: fetchScadaPntRealData(x))
# dump the results
gtMasterDf.to_excel('dumps/gt_dump.xlsx', index=False)
