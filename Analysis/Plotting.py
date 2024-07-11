import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import constants

myCmap=sns.diverging_palette(170, 330, l=65, center="dark", as_cmap=True)

def isValid(x, y):
    phases=['#','@','$']
    if x==y: return False
    elif 'Time' in x or 'Time' in y: return False
    elif x.strip('#@$')==y.strip('#@$'): return True
    for sym in phases:
        if sym in x and sym in y: return True
    
    return True

def getCorrValues(cor):
    corrList=[]
    for i in cor.index:
        for j in cor.columns:
            if not np.isnan(cor.loc[i,j]) and np.abs(cor.loc[i,j])>0.5:
                x=j.replace('_log','')
                y=i.replace('_log','')
                
                if isValid(x,y): corrList.append({'x': j, 'y': i})
    return [row['x'] for row in corrList], [row['y'] for row in corrList]

def corrGrid(df, xaxis, yaxis, tipo: str, barrera=0):
    xsor= xaxis.copy()
    ysor= yaxis.copy()
    xsor.sort()
    ysor.sort()

    if xsor==ysor: singleAxis=True
    else: singleAxis=False

    cor = df.loc[:,xsor if singleAxis else xsor+ysor].corr()
    cor=cor[cor.abs().ge(barrera)].loc[xsor,ysor].dropna(how='all').dropna(how='all', axis=1)

    fig = plt.figure(figsize=(8, 6))
    ax = sns.heatmap(cor, vmin=-1, vmax=1, annot=True, cmap=myCmap, linewidths=.5)
    ax.set_title(tipo.upper())
    return cor, fig

def plottingGrid(df, xaxis, yaxis, tipo, nameBase, focusList, plotType):
    for i, phys in enumerate(xaxis):
        fig, axs = plt.subplots(1, len(focusList), figsize=(5*len(focusList),4))
        fig.subplots_adjust(wspace=0.25,top=0.9)
        
        spec=yaxis[i]
        figName= '_'.join([nameBase+plotType+'/',tipo.replace(' ','').upper(),plotType,phys,spec])+'.png'

        for j, focus in enumerate(focusList):
            if plotType == constants.SCATTER:
                sns.scatterplot(df,x=phys,y=spec, ax=axs[j],
                                hue= focus, palette=sns.hls_palette(s=1, l=.4, h=j*.17, n_colors=3),
                                linewidth=0, legend='full',
                                alpha=0.5, s=15
                                )
            elif plotType == constants.BAND:
                sns.lineplot(data=df, x=phys,y=spec, ax=axs[j],
                             hue= focus, palette=sns.hls_palette(s=1, l=.4, h=j*.17, n_colors=3),
                             errorbar=lambda x: (x.min(), x.max()),
                             )
            sns.move_legend(axs[j], "upper center", bbox_to_anchor=(0.5, -0.15), ncol=3)

        fig.suptitle(tipo.upper())
        fig.savefig(figName, dpi=300, bbox_inches='tight')
        plt.close()

def jointPlot(df, xaxis, yaxis, tipo, nameBase, focusList):
    for i, phys in enumerate(xaxis):
        spec=yaxis[i]

        for j, focus in enumerate(focusList):
            f = sns.jointplot(df, x=spec,y=phys,
                            hue=focus, palette= sns.hls_palette(s=1, l=.4, h=j*.17, n_colors=3),
                            alpha=0.5, linewidth=0,
                            )
            f.plot_marginals(sns.histplot, alpha=0.5)
            sns.move_legend(f.figure.axes[0], "upper center", bbox_to_anchor=(0.5, -0.15), ncol=3)
            
            figName= '_'.join([nameBase+constants.JOINT+'/',tipo.replace(' ','').upper(),constants.JOINT,focus,phys,spec])+'.png'
            f.savefig(figName, dpi=300, bbox_inches='tight')
        plt.close()

def timePlot(df, prop, tipo, nameBase):
    fig, ax = plt.subplots(figsize=(7,5))
    fig.subplots_adjust(top=0.93)
    sns.lineplot(df, x='normalizedTime', y=prop, 
                 hue='runName', palette='hls', 
                 alpha=0.5, legend=None, ax=ax)
    ax.set_xscale('log')
    fig.suptitle(tipo.upper())

    figName= '_'.join([nameBase+tipo.replace(' ','').upper(),constants.TIME,prop])+'.png'
    fig.savefig(figName, dpi=300, bbox_inches='tight')
    plt.close()
