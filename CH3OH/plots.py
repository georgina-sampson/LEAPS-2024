# import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
# import pandas as pd
import constants, os, math
import Plotting as pl

folder = constants.folder
nameBase= folder.format('Plots/')
species=['CH3OH','#CH3OH']

df_sh = pl.buildDataframe(constants.SHOCK, constants.folder, constants.physical, species, singleDf=True)
df_hc = pl.buildDataframe(constants.HOTCORE, constants.folder, constants.physical, species, singleDf=True)
df_db = pl.buildDataframe([constants.SHOCK, constants.HOTCORE], constants.folder, constants.physical, species, singleDf=False)

# Comparison of Local Abundance
la_df=pl.localAbundanceDataframe(df_db, species, constants.physical, constants.BOTH, momento=constants.ALL, singleDf=False)
params=[constants.COSMICRAY, constants.INTERSTELLARRAD, constants.IDENS]

path_df= pl.abundanceComparison(la_df, params, params, nameBase+'abundanceComparison/subplots/', saveFig=True, returnFilepaths=True)

for focusParm in params:
    imList=list(path_df[path_df['hue' if focusParm==constants.IDENS else 'focus']==focusParm]['path'])
    pl.abundanceComparisonGrid(imList, 2, 2, focusParm, nameBase+'abundanceComparison/')

# Local Abundance Plots
# for tipo, m_df in {constants.HOTCORE: df_hc, constants.SHOCK: df_sh}.items():
#     for focus in constants.initparams[tipo]:
#         filePaths=pl.localAbundancePlot(m_df, focus, tipo, nameBase+'localAbundance/', returnFilepaths=True)
#         pl.localAbundanceGrid(filePaths, tipo, focus, nameBase+'localAbundance/', saveFig=True)

# Misc
# for tipo, dfi in {constants.HOTCORE: df_hc, constants.SHOCK: df_sh}.items():
#     df=pl.localAbundanceDataframe(dfi, species, constants.physical, tipo, momento=constants.ALL, singleDf=True)
#     pl.singleBox(df, 'zeta', 'abundance', 'species', tipo, nameBase, 'Abundance vs Cosmic Rays', saveFig=True, returnAx=False, figAx=None)
    
#     plotDict={'cols':['CH3OH', '#CH3OH'], 'rows':['gasTemp'], 'focusList':['zeta']*2}
#     pl.gridScatter(dfi, plotDict, tipo, 'Gas and Surface Methanol', nameBase, xbound=-6, saveFig=True)