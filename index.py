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
              'mp': 'Madhya Pradesh', 'cg': 'Chhattisgarh'}
messageStr = ''
for st in ['gj', 'mh', 'mp', 'cg']:
    stateHvBusMessage = hvDetector.generateMessage(st, isForHigh=True)
    stateOffBrsMessage = brsDetector.generateMessage(st, isOn=False)
    stateIctsMessage = ictsDetector.generateMessage(st, isFlowReverse=False)
    stateGtsMessage = gtsDetector.generateMessage(st, isFlowReverse=False)
    messageStr += '{0}\n{1}\n{2}\n{3}\n{4}\n\n\n'.format(stateNames[st], stateHvBusMessage,
                                                    stateOffBrsMessage, stateIctsMessage, stateGtsMessage)

with open(outFilePath, 'w') as f:
    f.write(messageStr)