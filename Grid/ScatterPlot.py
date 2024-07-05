import uclchem, os, constants
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

myCmap=sns.diverging_palette(170, 330, l=65, center="dark", as_cmap=True)

def makeDataframe(filePath: str, tdf):
    df = uclchem.analysis.read_output_file(filePath)
    fName=filePath.split('/')
    df['runName']=fName[-1]

    for prop in tdf.columns:
        if prop == constants.SHOCKVEL: df[prop]=tdf.at[filePath,prop]
    return df

def makeLog(df, columns):
    for c in columns:
        df[c]=np.log10(df[c])
    return df

def corrGrid(df, xaxis, yaxis, tipo: str, logxscale=False, logyscale=False):
    if logxscale: df=makeLog(df, xaxis)
    if logyscale: df=makeLog(df, yaxis)

    cor = df.loc[:,df.columns[:-1]].corr()
    cor=cor.loc[:,yaxis][len(yaxis):].dropna(how='all')
    fig = plt.figure(figsize=(8, 6))
    ax = sns.heatmap(cor, vmin=-1, vmax=1, annot=True, cmap=myCmap, linewidths=.5)
    ax.set_title(tipo.upper())
    if logxscale: ax.set_xlabel('log')
    if logyscale: ax.set_ylabel('log')
    return fig

def scatterGrid(df, xaxis, yaxis, title, logxscale=False, logyscale=False):
    fig, axs = plt.subplots(len(xaxis), len(yaxis), figsize=(len(yaxis)*5, len(xaxis)*5))
    fig.subplots_adjust(wspace=0.4, hspace=0.4)

    for i, spec in enumerate(xaxis):
        for j, phys in enumerate(yaxis):
            sns.scatterplot(df,x=spec,y=phys,ax=axs[i][j],
                            hue='runName', palette='Spectral', s=10,
                            legend= 'auto' if i==0 and j==int(np.ceil(len(yaxis)/2)-1) else None)
            if logxscale: axs[i][j].set_xscale('log')
            if logyscale: axs[i][j].set_yscale('log')
            if i==0 and j==int(np.ceil(len(yaxis)/2)-1): axs[i][j].legend(loc='upper center',ncols=len(df['runName'].unique()), bbox_to_anchor=(0.5, 1.2))
    
    fig.suptitle(title, size='xx-large')
    return fig

folder = '/data2/gsampsonolalde/LEAPS-2024/Grid/{}/{}/'
species=['#CH3OH', 'CH3OH', '@CH3OH', '#SIO', 'SIO', '@SIO']
physical=['Time', 'Density', 'gasTemp', 'av', 'zeta', 'radfield']

runs = {constants.SHOCK: '2024-07-01_124848', constants.HOTCORE: '2024-07-01_134429'}
logscales = [[False, False], ['log', False], [False, 'log'], ['log', 'log']]

for tipo in runs:
    if tipo == constants.SHOCK: physical.append(constants.SHOCKVEL)
    print(runs[tipo], tipo)
    tdf= pd.read_csv(folder.format(runs[tipo], "stage2_df.csv")[:-1], index_col=0)
    tdf.index = tdf['outputFile']
    li=[f for f in os.listdir(folder.format(runs[tipo], constants.PHASE2)) if 'startcollapse' not in f]
    df = pd.concat([makeDataframe(folder.format(runs[tipo], constants.PHASE2)+gg, tdf) for gg in li])
    df = df.loc[:,physical+species+['runName']]
    
    for logxscale, logyscale in logscales:
        print(logxscale)
        figName=folder.format('AnalysisPlots', tipo)+f'corrGrid{'_log' if logxscale else '_lin'}{'_log' if logyscale else '_lin'}.png'
        corrGrid(df, species, physical, tipo, logxscale, logyscale).savefig(figName, dpi=300, bbox_inches='tight')
        title=f'{tipo.upper()}{' log' if logxscale else ' lin'}{' log' if logyscale else ' lin'}'
        figName=folder.format('AnalysisPlots', tipo)+f'scatterGrid{'_log' if logxscale else '_lin'}{'_log' if logyscale else '_lin'}.png'
        scatterGrid(df, species, physical, title, logxscale=False, logyscale=False).savefig(figName, dpi=300, bbox_inches='tight')
