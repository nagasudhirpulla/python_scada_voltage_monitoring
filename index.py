import pandas as pd
import random
from state_hv_detector import StateHvDetector
from state_live_brs_detector import StateLiveBrsDetector
from state_ict_flows_detector import StateIctFlowsDetector
from state_gt_flows_detector import StateGtFlowsDetector

outFilePath = 'output.txt'

hvDetector = StateHvDetector('secret/scada_points.xlsx')
# stateHvBusInfo = hvDetector.getHvBusesInfoForState('gj', isForHigh=True)
# stateHvBusMessage = hvDetector.generateMessage('gj', isForHigh=True)

brsDetector = StateLiveBrsDetector('secret/scada_points.xlsx')
# stateOffBrsInfo = brsDetector.getBrsInfoForState('gj', isOn=False)
# stateOffBrsMessage = brsDetector.generateMessage('gj', isOn=False)

ictsDetector = StateIctFlowsDetector('secret/scada_points.xlsx')
# stateIctsInfo = ictsDetector.getIctsInfoForState('gj', isFlowReverse=True)
# stateIctsMessage = ictsDetector.generateMessage('gj', isFlowReverse=False)

gtsDetector = StateGtFlowsDetector('secret/scada_points.xlsx')
# stateGtsInfo = gtsDetector.getGtsInfoForState('gj', isFlowReverse=True)
# stateGtsMessage = gtsDetector.generateMessage('gj', isFlowReverse=False)

stateNames = {'gj': 'Gujarat', 'mh': 'Maharashtra',
              'mp': 'Madhya Pradesh', 'cg': 'Chhattisgarh', 'cs': 'Central Sector'}
messageStr = ''
stateRepLineSeparator = "-------------------------------------------"
for st in ['gj', 'mh', 'mp', 'cg', 'cs']:
    stateHvBusMessage = hvDetector.generateMessage(st, isForHigh=True)
    stateOffBrsMessage = brsDetector.generateMessage(st, isOn=False)
    stateIctsMessage = ictsDetector.generateMessage(st, isFlowReverse=True)
    stateGtsMessage = gtsDetector.generateMessage(st, isFlowReverse=False)
    messageStr += '{0} Substations Summary\n\n{1}\n\n{2}\n\n{3}\n\n{4}\n{5}\n\n'.format(stateNames[st], stateHvBusMessage,
                                                    stateOffBrsMessage, stateIctsMessage, stateGtsMessage, stateRepLineSeparator)
messageStr += """May please refer clause 5.2(S), 6.4.12, 6.6.3 in this regard.
Request to
1. Take up with concerned S/S to reduce MVAR flow from LV side to HV side by switching off capacitors,
2. To switch on all B/Rs and L/Rs
3. To absorb maximum Vars at all generating stations as per capability curve so as to maintain at least voltage reduced to 405kV on EHV side of generator bus.
4. To explore possibility of running more machines at Koyna Stage IV in condenser mode, presently two units are running in condenser mode.
5. To run mchines at Koyna stage-I & II in condenser mode
6. To take up with wind generators connected on LV side to operate in Voltage control mode not to generate VARs
7. And to implement Any other necessary measure to control voltages to safe values
"""
with open(outFilePath, 'w') as f:
    f.write(messageStr)
