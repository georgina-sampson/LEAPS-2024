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

# Local Abundance Plots
for tipo, m_df in {constants.HOTCORE: df_hc, constants.SHOCK: df_sh}.items():
    pl.checkFolders(nameBase+'localAbundance/')
    colorPalette=['#f72585','#2667ff','#004b23']

    for focus in constants.initparams[tipo]:
        for param in m_df[focus].unique():
            dfi=m_df[m_df[focus]==param]
            figName= '_'.join([nameBase+'localAbundance/'+tipo.replace(' ','').upper(),'abundance',focus,str(param)])+'.png'

            fig, axs = plt.subplots(figsize=(16,8))
            fig.subplots_adjust(top=0.95)
            for i, time in enumerate(constants.times[tipo]):
                df=pl.localAbundanceDataframe(dfi, constants.species, constants.physical, tipo, momento=time, singleDf=True)
                axs.scatter(df['runName'], df['abundance'], label=time,
                            c=colorPalette[i], s=50,
                            linewidth=0, alpha=0.75)

            axs.set_yscale('log')
            axs.set_ybound(1e-14,1e-4)
            axs.tick_params(axis='x', labelrotation=90)
            fig.legend(ncols=3, loc="upper right", bbox_to_anchor=(0.9, 1))

            fig.suptitle(f"CH3OH Abundance {tipo.upper()}: {focus}={param}")
            fig.savefig(figName, dpi=300, bbox_inches='tight')
            plt.close()

# Misc
# for tipo, dfi in {constants.HOTCORE: df_hc, constants.SHOCK: df_sh}.items():
#     df=pl.localAbundanceDataframe(dfi, species, constants.physical, tipo, momento=constants.ALL, singleDf=True)
#     pl.singleBox(df, 'zeta', 'abundance', 'species', tipo, nameBase, 'Abundance vs Cosmic Rays', saveFig=True, returnAx=False, figAx=None)
    
#     plotDict={'cols':['CH3OH', '#CH3OH'], 'rows':['gasTemp'], 'focusList':['zeta']*2}
#     pl.gridScatter(dfi, plotDict, tipo, 'Gas and Surface Methanol', nameBase, xbound=-6, saveFig=True)