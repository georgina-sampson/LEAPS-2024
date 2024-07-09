import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

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

def scatterGrid(df, xaxis, yaxis, title, logxscale=False, logyscale=False):
    fig, axs = plt.subplots(len(xaxis), len(yaxis), figsize=(len(yaxis)*4.5, len(xaxis)*4))
    fig.subplots_adjust(wspace=0.4, hspace=0.2, top=0.905)

    for i, spec in enumerate(xaxis):
        for j, phys in enumerate(yaxis):
            sns.scatterplot(df,x=spec,y=phys,ax=axs[i][j],
                            hue='runName', palette='Spectral', s=10,
                            legend= 'auto' if i==0 and j==int(np.ceil(len(yaxis)/2)-1) else None)
            if logxscale: axs[i][j].set_xscale('log')
            if logyscale: axs[i][j].set_yscale('log')
            if i==0 and j==int(np.ceil(len(yaxis)/2)-1): axs[i][j].legend(loc='upper center',ncols=6, bbox_to_anchor=(0.5, 1.6))
    
    fig.suptitle(title, size='xx-large')
    return fig