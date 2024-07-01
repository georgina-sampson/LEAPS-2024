import numpy as np
import pandas as pd
import GridModel as grid
import constants

t_start = grid.giveTime() 
# Stage 1
# gridParameters = {constants.FDENS: np.array([1e6,1e7,1e8]),
gridParameters = {constants.FDENS: np.array([1e3,1e4,1e5]),
                  constants.COSMICRAY: np.array([10, 1000]),
                  constants.INTERSTELLARRAD: np.array([3, 1000])}

stage1_df, folder, parmNum = grid.stage1(gridParameters)

# # Reload Stage 1
# folder = ''
# stage1_df, parmNum = grid.reload_stage1(gridParameters, folder)

grid.giveTime(t_start)

# # Hot Core
# gridParameters.pop(constants.FDENS)
# gridParameters.update({constants.IDENS: np.array([1e6,1e7,1e8]),
#                        constants.FTEMP: np.array([50,100,300])})
# tipo = constants.HOTCORE

# C Shock
gridParameters.pop(constants.FDENS)
gridParameters.update({constants.IDENS: np.array([1e3,1e4,1e5]),
                       constants.SHOCKVEL: np.array([10,25,40])})
tipo = constants.SHOCK

# Stage 2
dTime = grid.stage2(gridParameters, tipo, stage1_df, folder, parmNum)
grid.giveTime(t_start)