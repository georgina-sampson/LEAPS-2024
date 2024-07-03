import uclchem
import numpy as np
import pandas as pd
from multiprocessing import Pool
import os

folder='/data2/gsampsonolalde/LEAPS-2024/Tutorials'
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
result=model_table.apply(run_model, axis=1)

# Checking Your Grid
def element_check(output_file):
    df=uclchem.analysis.read_output_file(output_file)
    #get conservation values
    conserves=uclchem.analysis.check_element_conservation(df)
    #check if any error is greater than 1%
    return all([float(x[:-1])<1 for x in conserves.values()])

model_table["run_result"]=result
model_table["elements_conserved"]=model_table["outputFile"].map(element_check)
#check both conditions are met
model_table["Successful"]=(model_table.run_result>=0) & (model_table.elements_conserved)

model_table.head()