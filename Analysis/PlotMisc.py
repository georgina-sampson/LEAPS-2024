import constants, Plotting, os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# folder = '{}'
folder = constants.folder
nameBase= folder.format('MiscPlots/')

physical = constants.physical
species= constants.species

tipo = constants.SHOCK
xaxis='gasTemp_log'

df= Plotting.buildDataframe(tipo, folder, physical, species)
jointDf=Plotting.localAbundanceDataframe(df, species, physical, tipo, constants.ALL, singleDf=True)

Plotting.checkFolders(nameBase, [constants.ABUNDANCE+'/'])


figName= '_'.join([nameBase+constants.ABUNDANCE+'/'+tipo,constants.SCATTER,'methanol',xaxis,'zeta_log',constants.ABUNDANCE])+'.png'
g=sns.relplot(jointDf[(jointDf['species']=='#CH3OH_log')|(jointDf['species']=='CH3OH_log')],
            x=xaxis,y='abundance_log', col='zeta_log',
            hue='species', palette='hsv_r',
            linewidth=0, alpha=0.5, s=10)
g.figure.suptitle(tipo.upper())
g.figure.savefig(figName, dpi=300, bbox_inches='tight')
plt.close()


figName= '_'.join([nameBase+constants.ABUNDANCE+'/'+tipo,constants.SCATTER,'methanol',xaxis,constants.ABUNDANCE])+'.png'
fig, ax = plt.subplots(figsize=(7,7))

sns.scatterplot(jointDf[(jointDf['species']=='#CH3OH_log')|(jointDf['species']=='CH3OH_log')],
                x=xaxis,y='abundance_log', ax=ax,
                hue='species', palette='hsv_r',
                linewidth=0, alpha=0.5, s=10)
sns.move_legend(ax, "upper center", bbox_to_anchor=(0.5, -0.1), ncols=4)

ax.set_ybound(-14,-4)
ax.minorticks_on()
ax.set_title(tipo.upper())

fig.savefig(figName, dpi=300, bbox_inches='tight')
plt.close()