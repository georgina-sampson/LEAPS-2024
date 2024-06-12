import uclchem
import numpy as np
import pandas as pd
from multiprocessing import Pool
import os

folder='/data2/LEAPS-2024/Tutorials'
# This part can be substituted with any choice of grid
#here we just vary the density, temperature and zeta 
temperatures = np.linspace(10, 50, 3)
densities = np.logspace(4,6,3)
zetas = np.logspace(1, 3, 3)

#meshgrid will give all combinations, then we shape into columns and put into a table
parameterSpace = np.asarray(np.meshgrid(temperatures,densities,zetas)).reshape(3, -1)
model_table=pd.DataFrame(parameterSpace.T, columns=['temperature','density','zeta'])

#keep track of where each model output will be saved and make sure that folder exists
model_table["outputFile"]=model_table.apply(lambda row: f"{folder}/grid_folder/{row.temperature}_{row.density}_{row.zeta}.csv", axis=1)
print(f"{model_table.shape[0]} models to run")
if not os.path.exists(folder+"/grid_folder"):
    os.makedirs(folder+"/grid_folder")

def run_model(row):
    #basic set of parameters we'll use for this grid. 
    ParameterDictionary = {"endatfinaldensity":False,
                           "freefall": False,
                           "initialDens": row.density,
                           "initialTemp": row.temperature,
                           "zeta": row.zeta,
                           "outputFile": row.outputFile,
                           "finalTime":1.0e6,
                           "baseAv":10}
    result = uclchem.model.cloud(param_dict=ParameterDictionary)
    return result[0]#just the integer error code

# The Simple Way
# result=model_table.apply(run_model, axis=1)

# The Fast Way
def pool_func(x):
    i,row=x
    return run_model(row)

with Pool(processes=6) as pool:
    results = pool.map(pool_func, model_table.iterrows())