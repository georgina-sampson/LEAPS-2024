import numpy as np
import pandas as pd
import GridModel as grid

parameters = {'cosmicRay': np.array([10, 1000]),
              'interstellarRad': np.array([3, 1000])}

model_table = grid.setupGrid(parameters)
grid.phase1(model_table)

print(model_table)