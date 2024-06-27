import numpy as np
import pandas as pd
import GridModel as grid

gridParameters = {'cosmicRay': np.array([10, 1000]),
              'interstellarRad': np.array([3, 1000])}

phase1_df, folder = grid.setupGrid(gridParameters)
grid.phase1(phase1_df)


# Hot Core
gridParameters.update({'iDens':np.array([1e6,1e7,1e8]),
                       'fTemp': np.array([50,100,300])})
hotCore_df, folder = grid.setupGrid(gridParameters, phase1_df, folder)
grid.hotCore(hotCore_df)
