import constants, Plotting, os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# folder = '{}'
folder = '/data2/gsampsonolalde/LEAPS-2024/Analysis/{}'
nameBase= folder.format('AbundancePlots/')

physical = {constants.SHOCK: ['Density', 'gasTemp', 'av', 'zeta', 'radfield', constants.SHOCKVEL],
            constants.HOTCORE: ['Density', 'gasTemp', 'av', 'zeta', 'radfield']}
species=['#CH3OH', 'CH3OH', '#SIO', 'SIO']

def buildDataframe(tipo): 
    df= pd.read_csv(folder.format(tipo)+'.csv', index_col=0)

    df = df.loc[:,['Time']+physical[tipo]+species+['runName']]
    for prop in physical[tipo]+species:
        with np.errstate(divide='ignore'): df[f'{prop}_log']=np.log10(df[prop])
    
    df=df.reset_index().drop(columns=['index'])
    df=df.join(pd.DataFrame(df['runName'].str.replace('.dat','').str.split('_').values.tolist(),
                            columns=constants.initparams[tipo]), rsuffix='_str')
    return df

def finalAbundanceDataframe(df, especies=species):
    dfFinal=df.loc[df['normalizedTime'] == 1]

    campos=['runName', 'Density_log', 'gasTemp_log', 'av_log', 'zeta_log', 'radfield_log', 'cosmicRay', 'interstellarRad', 'iDens', 'fTemp', 'normalizedTime']

    tDic=dict([(key, []) for key in campos+['abundance_log', 'species']])
    for i in dfFinal.index:
        for spec in especies:
            tDic['abundance_log'].append(dfFinal.at[i,spec]) 
            tDic['species'].append(spec)
            for c in campos:
                tDic[c].append(dfFinal.at[i,c])
    return pd.DataFrame(tDic)

for tip in ['']:
    if not os.path.exists(nameBase+tip+'/'): os.makedirs(nameBase+tip+'/')

tipo=constants.HOTCORE
print(tipo)

df= buildDataframe(tipo)
df['normalizedTime']= df['Time']/df.groupby('runName')['Time'].transform('max')

dfFinal= finalAbundanceDataframe(df, [f'{prop}_log' for prop in species])
 
logPhysical= [f'{prop}_log' for prop in physical[tipo]]

for phys in logPhysical+['species']:
    Plotting.finalAbundancePlot(dfFinal, phys, tipo, nameBase)

plt.close()