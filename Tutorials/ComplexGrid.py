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
model_table["outputFile"]=model_table.apply(lambda row: f"{folder}/complex_grid_folder/{row.temperature}_{row.density}_{row.zeta}.csv", axis=1)
print(f"{model_table.shape[0]} models to run")
if not os.path.exists(folder+"/complex_grid_folder"):
    os.makedirs(folder+"/complex_grid_folder")

out_species=["CO","H2O","CH3OH"]

def run_prelim(density):
    #basic set of parameters we'll use for this grid. 
    ParameterDictionary = {"endatfinaldensity":True,
                           "freefall": True,
                           "initialDens":1e2,
                           "finalDens": density,
                           "initialTemp": 10.0,
                           "abundSaveFile": f"{folder}/complex_grid_folder/starts/{density:.0f}.csv",
                           "baseAv":1}
    result = uclchem.model.cloud(param_dict=ParameterDictionary)
    return result

def run_model(row):
    i,row=row # we know we're receiving the iterrows() tuple
    #basic set of parameters we'll use for this grid. 
    ParameterDictionary = {"endatfinaldensity":False,
                           "freefall": False,
                           "initialDens": row.density,
                           "initialTemp": 10.0,
                           "outputFile": row.outputFile,
                           "abundLoadFile": f"{folder}/complex_grid_folder/starts/{row.density:.0f}.csv",
                           "finalTime":1.0e5,
                           "abstol_factor":1e-18,
                           "reltol":1e-12,
                           "baseAv":1}
    result = uclchem.model.cshock(row.shock_velocity,param_dict=ParameterDictionary,out_species=out_species)
    #First check UCLCHEM's result flag to seeif it's positive, if it is return the abundances
    if result[0]>0:
        return result[:]
    #if not, return NaNs because model failed
    else:
        return([np.nan]*len(out_species))
    
# This part can be substituted with any choice of grid
# here we just combine various initial and final densities into an easily iterable array
shock_velocities = np.linspace(10, 50, 3)
densities = np.logspace(4,6,3)

parameterSpace = np.asarray(np.meshgrid(shock_velocities,densities)).reshape(2, -1)
model_table=pd.DataFrame(parameterSpace.T, columns=['shock_velocity','density'])
model_table["outputFile"]=model_table.apply(lambda row: f"{folder}/complex_grid_folder/shocks/{row.shock_velocity}_{row.density}.csv", axis=1)
print(f"{model_table.shape[0]} models to run")

for folder in ["starts","shocks"]:
    if not os.path.exists(f"{folder}/complex_grid_folder/{folder}"):
        os.makedirs(f"{folder}/complex_grid_folder/{folder}")
