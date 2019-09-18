import pandas as pd
import random
from state_hv_detector import StateHvDetector
from state_live_brs_detector import StateLiveBrsDetector
from state_ict_flows_detector import StateIctFlowsDetector
from state_gt_flows_detector import StateGtFlowsDetector

hvDetector = StateHvDetector('secret/scada_points.xlsx')
# stateHvBusInfo = hvDetector.getHvBusesInfoForState('gj', isForHigh=True)
hvBusMessage = hvDetector.generateMessage('gj', isForHigh=True)

brsDetector = StateLiveBrsDetector('secret/scada_points.xlsx')
# stateOffBrsInfo = brsDetector.getBrsInfoForState('gj', isOn=False)
stateOffBrsMessage = brsDetector.generateMessage('gj', isOn=False)

ictsDetector = StateIctFlowsDetector('secret/scada_points.xlsx')
# stateIctsInfo = ictsDetector.getIctsInfoForState('gj', isFlowReverse=True)
stateIctsMessage = ictsDetector.generateMessage('gj', isFlowReverse=True)

gtsDetector = StateGtFlowsDetector('secret/scada_points.xlsx')
# stateGtsInfo = gtsDetector.getGtsInfoForState('gj', isFlowReverse=True)
stateGtsMessage = gtsDetector.generateMessage('gj', isFlowReverse=True)
