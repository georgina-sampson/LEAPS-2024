import os, constants, uclchem
import pandas as pd

def makeDataframe(filePath: str, tdf):
    df = uclchem.analysis.read_output_file(filePath)
    fName=filePath.split('/')
    df['runName']=fName[-1]

    for prop in tdf.columns:
        if prop == constants.SHOCKVEL: df[prop]=tdf.at[filePath,prop]
    return df

folder = '/data2/gsampsonolalde/LEAPS-2024/Grid/{}/{}/'
# runs = {constants.SHOCK: '2024-07-01_124848', constants.HOTCORE: '2024-07-01_134429'}
runs={constants.HOTCORE: '2024-07-16_115707',
      constants.SHOCK: '2024-07-01_124848'}

for tipo in runs:
    tdf= pd.read_csv(folder.format(runs[tipo], "stage2_df.csv")[:-1], index_col=0)
    tdf.index = tdf['outputFile']
    li=[f for f in os.listdir(folder.format(runs[tipo], constants.PHASE2)) if 'startcollapse' not in f]
    df = pd.concat([makeDataframe(folder.format(runs[tipo], constants.PHASE2)+gg, tdf) for gg in li])
    df=df.reset_index()
    df.pop('index')

    df.to_csv('/data2/gsampsonolalde/LEAPS-2024/CH3OH/'+tipo+'.csv')