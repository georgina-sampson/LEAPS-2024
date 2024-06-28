import numpy as np
import pandas as pd
import GridModel as grid

# Stage 1
gridParameters = {'fDens':np.array([1e6,1e7,1e8]),
# gridParameters = {'fDens':np.array([1e3,1e4,1e5]),
                  'cosmicRay': np.array([10, 1000]),
                  'interstellarRad': np.array([3, 1000])}

# stage1_df, folder = grid.stage1(gridParameters)

# Reload Stage 1
folder = '/data2/LEAPS-2024/Grid/2024-06-28_141556/'
stage1_df = grid.reload_stage1(gridParameters, folder)

# Hot Core
gridParameters.update({'iDens':np.array([1e6,1e7,1e8]),
                       'fTemp': np.array([50,100,300])})
tipo = 'hot core'

# C Shock
# gridParameters.update({'iDens':np.array([1e3,1e4,1e5]),
#                        'shockVel': np.array([10,25,40])})
# tipo = 'c shock'

# Stage 2
dTime = grid.stage2(gridParameters, tipo, stage1_df, folder)