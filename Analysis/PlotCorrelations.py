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


for tip in [constants.SCATTER, constants.JOINT, constants.BAND, 'contVars']:
    if not os.path.exists(nameBase+'/species/'+tip+'/'): os.makedirs(nameBase+'/species/'+tip+'/')
    if not os.path.exists(nameBase+'/physical/'+tip+'/'): os.makedirs(nameBase+'/physical/'+tip+'/')

for singleAxis in [True, False]:
    print('singleAxis',singleAxis)
    subf= '/species/' if singleAxis else '/physical/'
    for tipo in physical:
        print(tipo)
        df= Plotting.buildDataframe(tipo, folder, physical, species)
        
        yaxis= [f'{prop}_log' for prop in species]
        if singleAxis: xaxis=yaxis
        else: xaxis= [f'{prop}_log' for prop in physical[tipo]]

        figName=nameBase+subf+tipo.replace(' ','').upper()+f"_{'species_' if singleAxis else ''}CorrGrid_log_log.png"
        corr, fig = Plotting.corrGrid(df, xaxis, yaxis, tipo, 0)

        xaxis, yaxis = Plotting.getCorrValues(corr)

        if len(xaxis)>0 and len(yaxis)>0:
            figName=nameBase+subf+tipo.replace(' ','').upper()+f"_{'species_' if singleAxis else ''}focusedCorrGrid_log_log.png"
            Plotting.corrGrid(df, list(set(xaxis)), list(set(yaxis)), tipo, 0.5)[1].savefig(figName, dpi=300, bbox_inches='tight')

            focusList = constants.initparams[tipo]
            for plotType in [constants.SCATTER, constants.BAND]:
                Plotting.plottingGrid(df, yaxis, xaxis, tipo, nameBase+subf, focusList, plotType)

            Plotting.jointPlot(df, xaxis, yaxis, tipo, nameBase+subf, focusList)
            plt.close()
            if singleAxis: Plotting.contScatterPlot(df, xaxis, yaxis, tipo, nameBase+subf, [f'{prop}_log' for prop in constants.varPhys[tipo]])
            plt.close()