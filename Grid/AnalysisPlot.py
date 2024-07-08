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

folder = '/data2/gsampsonolalde/LEAPS-2024/Grid/{}/{}/'
species=['#CH3OH', 'CH3OH', '@CH3OH', '#SIO', 'SIO', '@SIO']
runs = {constants.SHOCK: '2024-07-01_124848', constants.HOTCORE: '2024-07-01_134429'}

parametros = {
    constants.HOTCORE:{
        'xaxis': ['@CH3OH','@CH3OH','@CH3OH','@CH3OH','@CH3OH','@SIO','@SIO','@SIO','CH3OH','CH3OH','SIO','SIO','SIO','#CH3OH','#CH3OH','#CH3OH','#CH3OH','#CH3OH','#CH3OH','#CH3OH','#SIO','#SIO','#SIO'],
        'xlog': [True,True,True,True,False,False,True,True,True,True,False,False,True,True,True,True,False,False,True,False,True,True,True],
        'yaxis': ['@SIO','SIO','gasTemp','#SIO','Time','zeta','gasTemp','Time','zeta','#SIO','@SIO','gasTemp','Time','@CH3OH','@SIO','CH3OH','SIO','gasTemp','#SIO','Time','@SIO','SIO','gasTemp'],
        'ylog': [True,False,False,True,True,False,True,False,True,True,True,False,True,True,True,True,True,True,True,True,True,True,True]
    },
    constants.SHOCK:{
        'xaxis': ['@CH3OH','@CH3OH','@CH3OH','@SIO','CH3OH','CH3OH','CH3OH','CH3OH','#CH3OH','#CH3OH','#CH3OH','#CH3OH','#SIO','#SIO'],
        'xlog': [True,True,True,True,True,False,True,True,True,True,True,True,True,True],
        'yaxis': ['@SIO','gasTemp','#SIO','gasTemp','av','zeta','Density','SIO','@CH3OH','@SIO','gasTemp','#SIO','@SIO','gasTemp'],
        'ylog': [True,True,True,True,True,False,True,True,True,True,True,True,True,True]
    }
}

for tipo in runs:
    physical=['Time', 'Density', 'gasTemp', 'av', 'zeta', 'radfield']
    if tipo == constants.SHOCK: physical.append(constants.SHOCKVEL)

    tdf= pd.read_csv(folder.format(runs[tipo], "stage2_df.csv")[:-1], index_col=0)
    tdf.index = tdf['outputFile']
    li=[f for f in os.listdir(folder.format(runs[tipo], constants.PHASE2)) if 'startcollapse' not in f]
    df = pd.concat([makeDataframe(folder.format(runs[tipo], constants.PHASE2)+gg, tdf) for gg in li])
    df=df.reset_index()
    df.pop('index')
    df = df.loc[:,physical+species+['runName']]

    params=parametros[tipo]
    xaxis=params['xaxis']
    xlog=params['xlog']
    yaxis=params['yaxis']
    ylog=params['ylog']
    
    for i in range(len(xaxis)):
        fig = plt.figure(figsize=(8, 6))
        ax = sns.scatterplot(df,x=xaxis[i],y=yaxis[i],
                                # hue='runName', palette='Spectral', s=10,
                                legend= 'auto')
        if xlog: ax.set_xscale('log')
        if ylog: ax.set_yscale('log')
        
        figName = folder.format('AnalysisPlots', 'trial')+f"{tipo}_{xaxis[i]}_{'log' if xlog[i] else 'lin'}_{yaxis[i]}_{'log' if ylog[i] else 'lin'}.png"
        fig.suptitle(tipo, size='xx-large')
        fig.savefig(figName, dpi=300, bbox_inches='tight')
        plt.close()