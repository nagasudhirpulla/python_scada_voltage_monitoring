import pandas as pd
import random
from state_hv_detector import StateHvDetector
from state_live_brs_detector import StateLiveBrsDetector
from state_ict_flows_detector import StateIctFlowsDetector
from state_gt_flows_detector import StateGtFlowsDetector

hvDetector = StateHvDetector('secret/scada_points.xlsx')
stateHvBusInfo = hvDetector.getHvBusesInfoForState('gj')

brsDetector = StateLiveBrsDetector('secret/scada_points.xlsx')
stateOffBrsInfo = brsDetector.getBrsInfoForState('gj', isOn=False)

ictsDetector = StateIctFlowsDetector('secret/scada_points.xlsx')
stateIctsInfo = ictsDetector.getIctsInfoForState('gj')

gtsDetector = StateGtFlowsDetector('secret/scada_points.xlsx')
stateGtsInfo = gtsDetector.getGtsInfoForState('gj')
