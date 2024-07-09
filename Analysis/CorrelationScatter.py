import constants, Plotting
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

folder = '/data2/gsampsonolalde/LEAPS-2024/Analysis/{}'
physical = {constants.SHOCK: ['Time', 'Density', 'gasTemp', 'av', 'zeta', 'radfield', constants.SHOCKVEL],
            constants.HOTCORE: ['Time', 'Density', 'gasTemp', 'av', 'zeta', 'radfield']}
species=['#CH3OH', 'CH3OH', '#SIO', 'SIO']

for singleAxis in [True, False]:
    print('singleAxis',singleAxis)
    for tipo in physical:
        nameBase= folder.format('CorrelationScatterPlots/')+tipo.replace(' ','').upper()+'_'

        df= pd.read_csv(folder.format(tipo)+'.csv', index_col=0)
        df = df.loc[:,physical[tipo]+species+['runName']]
        for prop in physical[tipo]+species:
            with np.errstate(divide='ignore'): df[f'{prop}_log']=np.log10(df[prop])
        
        yaxis= [f'{prop}_log' for prop in species]
        if singleAxis: xaxis=yaxis
        else: xaxis= [f'{prop}_log' for prop in physical[tipo]]

        figName=nameBase+f"{'species_' if singleAxis else ''}CorrGrid_log_log.png"
        corr, fig = Plotting.corrGrid(df, xaxis, yaxis, tipo, 0)
        fig.savefig(figName, dpi=300, bbox_inches='tight')

        xaxis, yaxis = Plotting.getCorrValues(corr, singleAxis)

        figName=nameBase+f"{'species_' if singleAxis else ''}focusedCorrGrid_log_log.png"
        Plotting.corrGrid(df, xaxis, yaxis, tipo, 0.5).savefig(figName, dpi=300, bbox_inches='tight')

        figName=nameBase+f"{'species_' if singleAxis else ''}scatterGrid_log_log.png"
        Plotting.scatterGrid(df, xaxis, yaxis, tipo, True, True).savefig(figName, dpi=300, bbox_inches='tight')
        plt.close()