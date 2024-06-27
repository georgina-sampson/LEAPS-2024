import uclchem, os
import numpy as np
import pandas as pd
from datetime import datetime

def setupGrid(parameters: dict):
    ahora = str(datetime.now()).split('.')[0].replace(' ','_').replace(':','')
    folder = f'/data2/LEAPS-2024/Grid/{ahora}/'
    grid_folder = folder + 'data/'

    #meshgrid will give all combinations, then we shape into columns and put into a table
    parameterSpace = dynamicMesh(parameters)
    model_table=pd.DataFrame(parameterSpace.T, columns=parameters.keys())

    #keep track of where each model output will be saved and make sure that folder exists
    model_table["outputFile"]=model_table.apply(lambda row: f"{grid_folder}{'_'.join([str(row[key]) for key in model_table.columns])}.csv", axis=1)
    print(f"{model_table.shape[0]} models to run")

    os.makedirs(folder)
    os.makedirs(grid_folder)
    with open(folder+"Params.txt", "w") as f:
        for key in parameters.keys(): f.write(f"{key}: {', '.join(parameters[key])} \n")

    return model_table

def phase1(model_table):
    result = model_table.apply(run_modelCloud, axis=1)

    model_table["run_result"]=result
    model_table["elements_conserved"]=model_table["outputFile"].map(element_check)

    #check both conditions are met
    model_table["Successful"]=(model_table.run_result>=0) & (model_table.elements_conserved)

def run_modelCloud(row):
    #basic set of parameters we'll use for this grid. 
    ParameterDictionary = {"endatfinaldensity":False,
                           "freefall": False,
                           "initialTemp": 15,
                           "outputFile": row.outputFile,
                           "finalTime":1.0e6,
                           "baseAv":2}
    
    if 'iTemp' in row: ParameterDictionary['initialTemp']=row.iTemp
    if 'iDens' in row: ParameterDictionary['initialDens']=row.iDens
    if 'fDens' in row: ParameterDictionary['finalDens']=row.fDens
    if 'cosmicRay' in row: ParameterDictionary['zeta']=row.cosmicRay
    if 'interstellarRad' in row: ParameterDictionary['radfield']=row.interstellarRad
    if 'fTime' in row: ParameterDictionary['finalTime']=row.fTime
    if 'bAv' in row: ParameterDictionary['baseAv']=row.bAv

    result = uclchem.model.cloud(param_dict=ParameterDictionary)
    return result[0]

def run_modelShock(row):
    ParameterDictionary = {"endatfinaldensity":False,
                           "freefall": False,
                           "initialDens": row.density,
                           "initialTemp": 10.0,
                           "outputFile": row.outputFile,
                           "abundLoadFile": f"{folder}/complex_grid_folder/starts/{row.density:.0f}.csv",
                           "finalTime":1.0e5,
                           "abstol_factor":1e-18,
                           "reltol":1e-12,
                           "baseAv":2}
    result = uclchem.model.cshock(row.shock_velocity,param_dict=ParameterDictionary)
    #First check UCLCHEM's result flag to seeif it's positive, if it is return the abundances
    if result[0]>0:
        return result[:]
    #if not, return NaNs because model failed
    else:
        return([np.nan])

# Checking Your Grid
def element_check(output_file):
    df=uclchem.analysis.read_output_file(output_file)
    #get conservation values
    conserves=uclchem.analysis.check_element_conservation(df)
    #check if any error is greater than 1%
    return all([float(x[:-1])<1 for x in conserves.values()])

def dynamicMesh(parameters: dict):
    llaves=list(parameters.keys())
    
    if len(llaves) == 1: return np.asarray(np.meshgrid(parameters[llaves[0]])).reshape(len(llaves), -1)
    if len(llaves) == 2: return np.asarray(np.meshgrid(parameters[llaves[0]],parameters[llaves[1]])).reshape(len(llaves), -1)
    if len(llaves) == 3: return np.asarray(np.meshgrid(parameters[llaves[0]]),parameters[llaves[1]],parameters[llaves[2]]).reshape(len(llaves), -1)
    if len(llaves) == 4: return np.asarray(np.meshgrid(parameters[llaves[0]]),parameters[llaves[1]],parameters[llaves[2]],parameters[llaves[3]]).reshape(len(llaves), -1)
    if len(llaves) == 5: return np.asarray(np.meshgrid(parameters[llaves[0]]),parameters[llaves[1]],parameters[llaves[2]],parameters[llaves[3]],parameters[llaves[4]]).reshape(len(llaves), -1)
    if len(llaves) == 6: return np.asarray(np.meshgrid(parameters[llaves[0]]),parameters[llaves[1]],parameters[llaves[2]],parameters[llaves[3]],parameters[llaves[4]],parameters[llaves[5]]).reshape(len(llaves), -1)