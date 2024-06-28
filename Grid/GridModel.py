import uclchem, os
import numpy as np
import pandas as pd
from datetime import datetime

def stage1(gridParameters):
    print('Stage 1 - start')
    stage1_df, folder = setupGrid(gridParameters)
    print('grid setup done')

    print('Cloud - start')
    result = stage1_df.apply(run_modelCloud, axis=1)

    stage1_df["run_result"]=result
    stage1_df["elements_conserved"]=stage1_df["outputFile"].map(element_check)

    #check both conditions are met
    stage1_df["Successful"]=(stage1_df.run_result>=0) & (stage1_df.elements_conserved)
    print('Stage 1 - end')
    return stage1_df, folder

def stage2(gridParameters, tipo: str, stage1_df, folder: str):
    print('Stage 2 - start')
    stage2_df, folder = setupGrid(gridParameters, stage1_df, folder)
    print('grid setup done')

    if tipo == 'hot core': hotCore(stage2_df)
    elif tipo == 'c shock':
        dissipation_time = cShock(stage2_df)
        print(f'dissipation time: {dissipation_time}')
        with open(folder+"dissipation_time.txt", "w") as f:
            f.write(str(dissipation_time))

    else: return TypeError
    print('Stage 2 - end')

def reload_stage1(gridParameters, folder):
    print('reloading Phase 1 data')
    stage1_df, trash = setupGrid(gridParameters, folder=folder)
    return stage1_df

def setupGrid(parameters: dict, prevModel = pd.DataFrame({'vacio' : []}), folder=None):
    print('setupGrid - start')
    if not folder:
        ahora = str(datetime.now()).split('.')[0].replace(' ','_').replace(':','')
        folder = f'/data2/LEAPS-2024/Grid/{ahora}/'

    stage1= True if prevModel.empty == True else False
    grid_folder = folder+'startData/' if stage1 else folder+'modelData/'
    print(f'Folder: {grid_folder}')

    #meshgrid will give all combinations, then we shape into columns and put into a table
    parameterSpace = dynamicMesh(parameters)
    model_table=pd.DataFrame(parameterSpace.T, columns=parameters.keys())

    #keep track of where each model output will be saved and make sure that folder exists
    model_table["outputFile"]=model_table.apply(lambda row: f"{grid_folder}{'_'.join([str(row[key]) for key in model_table.columns])}.dat", axis=1)
    if stage1: model_table["abundSaveFile"]=model_table.apply(lambda row: f"{grid_folder}startcollapse{'_'.join([str(row[key]) for key in model_table.columns[:-1]])}.dat", axis=1)
    else: model_table["abundLoadFile"]=model_table.apply(lambda row: f"{folder}startData/startcollapse{'_'.join([str(row[key.replace('fDens','iDens')]) for key in prevModel.columns[:-2]])}.dat", axis=1)
    print(f"{model_table.shape[0]} models to run")

    if not os.path.exists(folder): os.makedirs(folder)
    if not os.path.exists(grid_folder): os.makedirs(grid_folder)

    with open(folder+"params.txt", "w") as f:
        f.write(f"Stage {1 if stage1 else 2} \n")
        for key in parameters.keys(): f.write(f"{key}: {', '.join([str(row) for row in parameters[key]])} \n")

    print('setupGrid - end')
    return model_table, folder

def hotCore(model_table):
    print('Hot Core - start')
    result = model_table.apply(run_modelHotCore, axis=1)

    model_table["run_result"]=result
    model_table["elements_conserved"]=model_table["outputFile"].map(element_check)

    #check both conditions are met
    model_table["Successful"]=(model_table.run_result>=0) & (model_table.elements_conserved)    
    print('Hot Core - end')

def cShock(model_table):
    print('C Shock - start')
    result, dissipation_time = model_table.apply(run_modelShock, axis=1)

    model_table["run_result"]=result
    model_table["elements_conserved"]=model_table["outputFile"].map(element_check)

    #check both conditions are met
    model_table["Successful"]=(model_table.run_result>=0) & (model_table.elements_conserved)    
    print('C Shock - end')
    return dissipation_time

def run_modelCloud(row):
    ParameterDictionary = {"initialTemp": 15.0,
                           "finalTime":1.0e6,
                           "baseAv":2.0,
                           "rout": 0.5,
                           "endatfinaldensity":False,
                           "freefall": True,
                           "outputFile": row.outputFile,
                           "abundSaveFile": row.abundSaveFile}
    
    if 'iTemp' in row: ParameterDictionary['initialTemp']=row.iTemp
    if 'iDens' in row: ParameterDictionary['initialDens']=row.iDens
    if 'fDens' in row:
        ParameterDictionary['finalDens']=row.fDens
        ParameterDictionary['endatfinaldensity']=True
    if 'cosmicRay' in row: ParameterDictionary['zeta']=row.cosmicRay
    if 'interstellarRad' in row: ParameterDictionary['radfield']=row.interstellarRad
    if 'fTime' in row: ParameterDictionary['finalTime']=row.fTime
    if 'rout' in row: ParameterDictionary['rout']=row.rout
    if 'bAv' in row: ParameterDictionary['baseAv']=row.bAv

    result = uclchem.model.cloud(param_dict=ParameterDictionary)
    return result[0]

def run_modelHotCore(row):
    ParameterDictionary = {"initialTemp": 15.0,
                           "finalTime":1.0e6,
                           "baseAv":2.0,
                           "freezeFactor": 0.0,
                           "rout": 0.5,
                           "freefall": False,
                           "endAtFinalDensity": False,
                           "outputFile": row.outputFile,
                           "abundLoadFile": row.abundLoadFile}
    
    if 'iTemp' in row: ParameterDictionary['initialTemp']=row.iTemp
    if 'iDens' in row: ParameterDictionary['initialDens']=row.iDens
    if 'fDens' in row:
        ParameterDictionary['finalDens']=row.fDens
        ParameterDictionary['endAtFinalDensity']=True
    if 'cosmicRay' in row: ParameterDictionary['zeta']=row.cosmicRay
    if 'interstellarRad' in row: ParameterDictionary['radfield']=row.interstellarRad
    if 'fTime' in row: ParameterDictionary['finalTime']=row.fTime
    if 'rout' in row: ParameterDictionary['rout']=row.rout
    if 'bAv' in row: ParameterDictionary['baseAv']=row.bAv

    result=uclchem.model.hot_core(temp_indx=3,max_temperature=row.fTemp,param_dict=ParameterDictionary)
    return result[0]

def run_modelShock(row):
    ParameterDictionary = {"initialTemp": 15.0,
                           "finalTime":1.0e6,
                           "baseAv":2.0,
                           "rout": 0.5,
                           "freefall": False,
                           "endAtFinalDensity": False,
                           "outputFile": row.outputFile,
                           "abundLoadFile": row.abundLoadFile,
                        #    "abstol_factor":1e-18,
                        #    "reltol":1e-12
                           }
    
    if 'iTemp' in row: ParameterDictionary['initialTemp']=row.iTemp
    if 'iDens' in row: ParameterDictionary['initialDens']=row.iDens
    if 'fDens' in row:
        ParameterDictionary['finalDens']=row.fDens
        ParameterDictionary['endAtFinalDensity']=True
    if 'cosmicRay' in row: ParameterDictionary['zeta']=row.cosmicRay
    if 'interstellarRad' in row: ParameterDictionary['radfield']=row.interstellarRad
    if 'fTime' in row: ParameterDictionary['finalTime']=row.fTime
    if 'rout' in row: ParameterDictionary['rout']=row.rout
    if 'bAv' in row: ParameterDictionary['baseAv']=row.bAv

    result = uclchem.model.cshock(shock_vel=row.shock_velocity,param_dict=ParameterDictionary)
    #First check UCLCHEM's result flag to seeif it's positive, if it is return the abundances
    if result[0]>0: return result[:]
    #if not, return NaNs because model failed
    else: return([np.nan])

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
    if len(llaves) == 3: return np.asarray(np.meshgrid(parameters[llaves[0]],parameters[llaves[1]],parameters[llaves[2]])).reshape(len(llaves), -1)
    if len(llaves) == 4: return np.asarray(np.meshgrid(parameters[llaves[0]],parameters[llaves[1]],parameters[llaves[2]],parameters[llaves[3]])).reshape(len(llaves), -1)
    if len(llaves) == 5: return np.asarray(np.meshgrid(parameters[llaves[0]],parameters[llaves[1]],parameters[llaves[2]],parameters[llaves[3]],parameters[llaves[4]])).reshape(len(llaves), -1)
    if len(llaves) == 6: return np.asarray(np.meshgrid(parameters[llaves[0]],parameters[llaves[1]],parameters[llaves[2]],parameters[llaves[3]],parameters[llaves[4]],parameters[llaves[5]])).reshape(len(llaves), -1)