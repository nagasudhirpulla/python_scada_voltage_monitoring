import pandas as pd
import random
from state_hv_detector import StateHvDetector

hvDetector = StateHvDetector('secret/scada_points.xlsx')
stateHvBusInfo = hvDetector.getHvBusesInfoForState('gj')