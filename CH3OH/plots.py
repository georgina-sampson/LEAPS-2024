# import numpy as np
# import matplotlib.pyplot as plt, matplotlib.colors as colors
# from matplotlib.gridspec import GridSpec
# import seaborn as sns
# import pandas as pd
import constants, os, math
import Plotting as pl

folder = constants.folder
nameBase= folder.format('Plots/')
species=['CH3OH','#CH3OH']

df_sh = pl.buildDataframe(constants.SHOCK, constants.folder, constants.physical, species, singleDf=True)
df_hc = pl.buildDataframe(constants.HOTCORE, constants.folder, constants.physical, species, singleDf=True)
df_db = pl.buildDataframe([constants.SHOCK, constants.HOTCORE], constants.folder, constants.physical, species, singleDf=False)

# Contiuity Plots
for tipo, df in {constants.HOTCORE: df_hc, constants.SHOCK: df_sh}.items():
    for runN in df['runName'].unique():
        pl.continuityPlot(df, runN, species, tipo, nameBase+f'subplots/{tipo}/', saveFig=True)
    
    imList=[nameBase+f'subplots/{tipo}/'+p for p in os.listdir(nameBase+f'subplots/{tipo}/') ]
    pl.continuityGrid(imList, tipo, nameBase, saveFig=True)


# for tipo, dfi in {constants.HOTCORE: df_hc, constants.SHOCK: df_sh}.items():
#     df=pl.localAbundanceDataframe(dfi, species, constants.physical, tipo, momento=constants.ALL, singleDf=True)
#     pl.singleBox(df, 'zeta', 'abundance', 'species', tipo, nameBase, 'Abundance vs Cosmic Rays', saveFig=True, returnAx=False, figAx=None)
    
#     plotDict={'cols':['CH3OH', '#CH3OH'], 'rows':['gasTemp'], 'focusList':['zeta']*2}
#     pl.gridScatter(dfi, plotDict, tipo, 'Gas and Surface Methanol', nameBase, xbound=-6, saveFig=True)