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

def localAbundancePlot(m_df, focus, tipo, nameBase, returnFilepaths=False):
    pl.checkFolders(nameBase)
    colorPalette=['#f72585','#2667ff','#004b23']
    markers=['d','s','o']
    filePaths=[]

    for param in m_df[focus].unique():
        dfi=m_df[m_df[focus]==param]
        figName= '_'.join([nameBase+tipo.replace(' ','').upper(),'abundance',focus,str(param)])+'.png'

        fig, axs = plt.subplots(figsize=(16,8))
        fig.subplots_adjust(top=0.95)
        for i, time in enumerate(constants.times[tipo]):
            df=pl.localAbundanceDataframe(dfi, constants.species, constants.physical, tipo, momento=time, singleDf=True)
            axs.scatter(df['runName'], df['abundance'], label=time,
                        c=colorPalette[i], s=50, marker=markers[i],
                        linewidth=0, alpha=0.75)

        axs.set_yscale('log')
        axs.set_ybound(1e-14,1e-4)
        axs.tick_params(axis='x', labelrotation=90)
        fig.legend(ncols=3, loc="upper right", bbox_to_anchor=(0.9, 1))

        fig.suptitle(f"CH3OH Abundance {tipo.upper()}: {focus}={param}",ha='right')
        fig.savefig(figName, dpi=300, bbox_inches='tight')
        plt.close()
        if returnFilepaths: filePaths.append(figName)
    if returnFilepaths: return filePaths

def plotGrid(imList, tipo, focus, nameBase, saveFig=True):
    pl.checkFolders(nameBase)
    figName= '_'.join([nameBase+tipo.replace(' ','').upper(),constants.ABUNDANCE, focus])+'.png'
    focusLen=len(imList)

    fig, axs = plt.subplots(1,focusLen, figsize=(4*focusLen,3))
    fig.subplots_adjust(top=0.95, hspace=0, wspace=0)

    for i, image_file in enumerate(imList):
        ax=axs[i]
        image = plt.imread(image_file)
        ax.imshow(image)
        ax.axis('off')
    
    fig.suptitle('Local Abundance Plot '+tipo.upper())
    if saveFig: fig.savefig(figName, dpi=300, bbox_inches='tight')
    plt.close()


# Local Abundance Plots
for tipo, m_df in {constants.HOTCORE: df_hc, constants.SHOCK: df_sh}.items():
    for focus in constants.initparams[tipo]:
        filePaths=localAbundancePlot(m_df, focus, tipo, nameBase+'localAbundance/', returnFilepaths=True)
        plotGrid(filePaths, tipo, focus, nameBase+'localAbundance/', saveFig=True)


# Misc
# for tipo, dfi in {constants.HOTCORE: df_hc, constants.SHOCK: df_sh}.items():
#     df=pl.localAbundanceDataframe(dfi, species, constants.physical, tipo, momento=constants.ALL, singleDf=True)
#     pl.singleBox(df, 'zeta', 'abundance', 'species', tipo, nameBase, 'Abundance vs Cosmic Rays', saveFig=True, returnAx=False, figAx=None)
    
#     plotDict={'cols':['CH3OH', '#CH3OH'], 'rows':['gasTemp'], 'focusList':['zeta']*2}
#     pl.gridScatter(dfi, plotDict, tipo, 'Gas and Surface Methanol', nameBase, xbound=-6, saveFig=True)