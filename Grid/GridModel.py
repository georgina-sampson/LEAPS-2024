import uclchem, os, constants
import numpy as np
import pandas as pd
from datetime import datetime
from time import process_time 

def stage1(gridParameters):
    print('Stage 1 - start')
    parmNum = len(gridParameters.keys())
    stage1_df, folder = setupGrid(gridParameters)
    print('grid setup done')

    print('Cloud - start')
    result = stage1_df.apply(run_modelCloud, axis=1)

    stage1_df["run_result"]=result
    stage1_df["elements_conserved"]=stage1_df["outputFile"].map(element_check)

    #check both conditions are met
    stage1_df["Successful"]=(stage1_df.run_result>=0) & (stage1_df.elements_conserved)
    stage1_df.to_csv(f'{folder}stage1_df.csv')
    print('Stage 1 - end')
    return stage1_df, folder, parmNum

def stage2(gridParameters, tipo: str, stage1_df, folder: str, prevParamNum: int):
    print('Stage 2 - start')
    stage2_df, folder = setupGrid(gridParameters, stage1_df, folder, prevParamNum)
    print('grid setup done')

    if tipo == constants.HOTCORE: final_df = hotCore(stage2_df)
    elif tipo == constants.SHOCK: final_df = cShock(stage2_df)
    else: return TypeError
    final_df.to_csv(f'{folder}stage2_df.csv')
    print('Stage 2 - end')

def reload_stage1(gridParameters, folder):
    print('reloading Stage 1 data')
    parmNum = len(gridParameters.keys())
    stage1_df, trash = setupGrid(gridParameters, folder=folder)
    return stage1_df, parmNum

def setupGrid(parameters: dict, prevModel = pd.DataFrame({'vacio' : []}), folder=None, prevParamNum = None):
    print('setupGrid - start')
    if not folder:
        ahora = str(datetime.now()).split('.')[0].replace(' ','_').replace(':','')
        folder = f'/data2/gsampsonolalde/LEAPS-2024/Grid/{ahora}/'

    stage1= True if prevModel.empty == True else False
    grid_folder = folder+'startData/' if stage1 else folder+'modelData/'
    print(f'Folder: {grid_folder}')

    #meshgrid will give all combinations, then we shape into columns and put into a table
    parameterSpace = dynamicMesh(parameters)
    model_table=pd.DataFrame(parameterSpace.T, columns=parameters.keys())

    #keep track of where each model output will be saved and make sure that folder exists
    model_table["outputFile"]=model_table.apply(lambda row: f"{grid_folder}{'_'.join([str(row[key]) for key in model_table.columns])}.dat", axis=1)
    if stage1: model_table["abundSaveFile"]=model_table.apply(lambda row: f"{grid_folder}startcollapse{'_'.join([str(row[key]) for key in model_table.columns[:len(parameters.keys())]])}.dat", axis=1)
    else: model_table["abundLoadFile"]=model_table.apply(lambda row: f"{folder}startData/startcollapse{'_'.join([str(row[key.replace(constants.FDENS,constants.IDENS)]) for key in prevModel.columns[:prevParamNum]])}.dat", axis=1)
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
    return model_table

def cShock(model_table):
    print('C Shock - start')
    model_table = model_table.apply(run_modelShock, axis=1)

    model_table["elements_conserved"]=model_table["outputFile"].map(element_check)

    #check both conditions are met
    model_table["Successful"]=(model_table.run_result>=0) & (model_table.elements_conserved)    
    print('C Shock - end')
    return model_table

def run_modelCloud(row):
    ParameterDictionary = {"initialTemp": 15.0,
                           "finalTime":1.0e6,
                           "baseAv":2.0,
                           "rout": 0.5,
                           "endatfinaldensity":False,
                           "freefall": True,
                           "outputFile": row.outputFile,
                           "abundSaveFile": row.abundSaveFile}
    
    if constants.ITEMP in row: ParameterDictionary['initialTemp']=row.iTemp
    if constants.IDENS in row: ParameterDictionary['initialDens']=row.iDens
    if constants.FDENS in row:
        ParameterDictionary['finalDens']=row.fDens
        ParameterDictionary['endatfinaldensity']=True
    if constants.COSMICRAY in row: ParameterDictionary['zeta']=row.cosmicRay
    if constants.INTERSTELLARRAD in row: ParameterDictionary['radfield']=row.interstellarRad
    if constants.FTIME in row: ParameterDictionary['finalTime']=row.fTime
    if constants.ROUT in row: ParameterDictionary[constants.ROUT]=row.rout
    if constants.BAV in row: ParameterDictionary['baseAv']=row.bAv

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
    
    if constants.ITEMP in row: ParameterDictionary['initialTemp']=row.iTemp
    if constants.IDENS in row: ParameterDictionary['initialDens']=row.iDens
    if constants.FDENS in row:
        ParameterDictionary['finalDens']=row.fDens
        ParameterDictionary['endAtFinalDensity']=True
    if constants.COSMICRAY in row: ParameterDictionary['zeta']=row.cosmicRay
    if constants.INTERSTELLARRAD in row: ParameterDictionary['radfield']=row.interstellarRad
    if constants.FTIME in row: ParameterDictionary['finalTime']=row.fTime
    if constants.ROUT in row: ParameterDictionary[constants.ROUT]=row.rout
    if constants.BAV in row: ParameterDictionary['baseAv']=row.bAv

    print(ParameterDictionary["outputFile"])
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
    
    if constants.ITEMP in row: ParameterDictionary['initialTemp']=row.iTemp
    if constants.IDENS in row: ParameterDictionary['initialDens']=row.iDens
    if constants.FDENS in row:
        ParameterDictionary['finalDens']=row.fDens
        ParameterDictionary['endAtFinalDensity']=True
    if constants.COSMICRAY in row: ParameterDictionary['zeta']=row.cosmicRay
    if constants.INTERSTELLARRAD in row: ParameterDictionary['radfield']=row.interstellarRad
    if constants.FTIME in row: ParameterDictionary['finalTime']=row.fTime
    if constants.ROUT in row: ParameterDictionary[constants.ROUT]=row.rout
    if constants.BAV in row: ParameterDictionary['baseAv']=row.bAv

    result, dissTime = uclchem.model.cshock(shock_vel=row.shockVel,param_dict=ParameterDictionary)
    row["run_result"]=result
    row["dissipation_time"]=dissTime
    return row

# Rename file
def checkFile(filePath):
    if not os.path.exists(filePath):
        newName=filePath.split('/')[-1]
        fold=filePath.split(newName)[0]
        tL= [f for f in os.listdir(fold) if newName.split('.dat')[0] in f]
        oldFileName=tL[0]
        os.rename(fold+oldFileName, filePath)

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

def giveTime(t_0 = None):
    if t_0:
        t_f = process_time() - t_0
        tH, tM, tS = [np.floor(t_f/3600), np.floor((t_f % 3600)/ 60), np.round((t_f % 3600) % 60, 1)]
        tiempo = f'{tH} hours   ' if tH > 0 else ''
        tiempo += f'{tM} minutes   ' if tM > 0 else ''
        tiempo += f'{tS} seconds   elapsed'
        print(tiempo)
    else: return process_time()