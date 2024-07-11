import constants, Plotting, os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# folder = '{}'
folder = '/data2/gsampsonolalde/LEAPS-2024/Analysis/{}'
nameBase= folder.format('TimePlots/')

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

for tip in ['physical', 'species']:
    if not os.path.exists(nameBase+tip+'/'): os.makedirs(nameBase+tip+'/')

for tipo in physical:
    print(tipo)
    focusList=constants.initparams[tipo]

    df= buildDataframe(tipo)
    df['normalizedTime']= df['Time']/df.groupby('runName')['Time'].transform('max')
 
    yaxis= [f'{prop}_log' for prop in species]
    xaxis= [f'{prop}_log' for prop in physical[tipo]]

    for phys in xaxis:
        Plotting.timePlot(df, phys, tipo, nameBase+'physical/')
    
    for spec in yaxis:
        Plotting.timePlot(df, spec, tipo, nameBase+'species/')

    plt.close()