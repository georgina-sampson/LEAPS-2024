import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

myCmap=sns.diverging_palette(170, 330, l=65, center="dark", as_cmap=True)

def corrGrid(df, xaxis, yaxis, tipo: str, barrera=0):
    if xaxis==yaxis: singleAxis=True
    else: singleAxis=False

    if singleAxis:
        cor = df.loc[:,xaxis].corr()
        cor=cor[cor.abs().ge(barrera)].dropna(how='all')
    else:
        cor = df.loc[:,xaxis+yaxis].corr()
        cor=cor[cor.abs().ge(barrera)].loc[xaxis,yaxis].dropna(how='all')

    fig = plt.figure(figsize=(8, 6))
    ax = sns.heatmap(cor, vmin=-1, vmax=1, annot=True, cmap=myCmap, linewidths=.5)
    ax.set_title(tipo.upper())
    return fig

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