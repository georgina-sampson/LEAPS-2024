import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import constants

myCmap=sns.diverging_palette(170, 330, l=65, center="dark", as_cmap=True)

def isValid(x, y):
    phases=['#','@','$']
    if x==y: return False
    elif x.strip('#@$')==y.strip('#@$'): return True
    for sym in phases:
        if sym in x and sym in y: return True
    return False

def getCorrValues(cor, singleAxis):
    corrList=[]
    for i in cor.index:
        for j in cor.columns:
            if not np.isnan(cor.loc[i,j]) and np.abs(cor.loc[i,j])>0.5:
                x=j.replace('_log','')
                y=i.replace('_log','')
                if singleAxis:
                    if isValid(x,y): corrList.append({'x': j, 'y': i})
                else: corrList.append({'x': j, 'y': i})
    return [row['x'] for row in corrList], [row['y'] for row in corrList]

def corrGrid(df, xaxis, yaxis, tipo: str, barrera=0):
    if xaxis==yaxis: singleAxis=True
    else: singleAxis=False

    cor = df.loc[:,xaxis if singleAxis else xaxis+yaxis].corr()
    cor=cor[cor.abs().ge(barrera)].loc[xaxis,yaxis].dropna(how='all').dropna(how='all', axis=1)

    fig = plt.figure(figsize=(8, 6))
    ax = sns.heatmap(cor, vmin=-1, vmax=1, annot=True, cmap=myCmap, linewidths=.5)
    ax.set_title(tipo.upper())
    return cor, fig

def scatterGrid(df, xaxis, yaxis, tipo):
    cosmicRay, interstellarRad, iDens, propio = constants.initparams[tipo]
    for i, phys in enumerate(xaxis):
        fig = plt.figure()
        ax=fig.add_subplot(111)

        spec=yaxis[i]
        figName=tipo.upper()+phys+'_'+spec+'_'+'.png'

        ax=sns.scatterplot(df,x=phys,y=spec,
                        hue= propio, style= iDens,
                        palette='Spectral', linewidth=0, size=15
                        )
        ax.legend(loc='upper right',ncols=6, bbox_to_anchor=(1, 1.1))
        ax.set_title(tipo.upper(), loc='left')
        fig.savefig(figName, dpi=300, bbox_inches='tight')
        plt.close()