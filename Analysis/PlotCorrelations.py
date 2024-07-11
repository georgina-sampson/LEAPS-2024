import constants, Plotting, os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# folder = '{}'
folder = '/data2/gsampsonolalde/LEAPS-2024/Analysis/{}'

nameBase= folder.format('CorrelationPlots/')
physical = {constants.SHOCK: ['Density', 'gasTemp', 'av', 'zeta', 'radfield', constants.SHOCKVEL],
            constants.HOTCORE: ['Density', 'gasTemp', 'av', 'zeta', 'radfield']}
species=['#CH3OH', 'CH3OH', '#SIO', 'SIO']

def buildDataframe(tipo): 
    df= pd.read_csv(folder.format(tipo)+'.csv', index_col=0)

    df = df.loc[:,physical[tipo]+species+['runName']]
    for prop in physical[tipo]+species:
        with np.errstate(divide='ignore'): df[f'{prop}_log']=np.log10(df[prop])
    
    df=df.reset_index().drop(columns=['index'])
    df=df.join(pd.DataFrame(df['runName'].str.replace('.dat','').str.split('_').values.tolist(),
                            columns=constants.initparams[tipo]), rsuffix='_str')
    return df

for tip in [constants.SCATTER, constants.JOINT, constants.BAND]:
    if not os.path.exists(nameBase+tip+'/'): os.makedirs(nameBase+tip+'/')

for singleAxis in [True, False]:
    print('singleAxis',singleAxis)
    for tipo in physical:
        print(tipo)
        focusList=constants.initparams[tipo]

        df= buildDataframe(tipo)
        
        yaxis= [f'{prop}_log' for prop in species]
        if singleAxis: xaxis=yaxis
        else: xaxis= [f'{prop}_log' for prop in physical[tipo]]

        figName=nameBase+tipo.replace(' ','').upper()+f"_{'species_' if singleAxis else ''}CorrGrid_log_log.png"
        corr, fig = Plotting.corrGrid(df, xaxis, yaxis, tipo, 0)

        xaxis, yaxis = Plotting.getCorrValues(corr)

        if len(xaxis)>0 and len(yaxis)>0:
            figName=nameBase+tipo.replace(' ','').upper()+f"_{'species_' if singleAxis else ''}focusedCorrGrid_log_log.png"
            Plotting.corrGrid(df, list(set(xaxis)), list(set(yaxis)), tipo, 0.5)[1].savefig(figName, dpi=300, bbox_inches='tight')

            for plotType in [constants.SCATTER, constants.BAND]:
                Plotting.plottingGrid(df, yaxis, xaxis, tipo, nameBase, focusList, plotType)

            Plotting.jointPlot(df, xaxis, yaxis, tipo, nameBase, focusList)

        plt.close()