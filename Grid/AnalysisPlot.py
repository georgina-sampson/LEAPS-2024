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

params = {
    constants.HOTCORE:{
        'xaxis': ['@CH3OH','@CH3OH','zeta','zeta','CH3OH','gasTemp','gasTemp','gasTemp','gasTemp','gasTemp','#CH3OH','#CH3OH','#CH3OH','#CH3OH','#CH3OH','#SIO','#SIO','Time','Time','Time'],
        'xlog': ['log','log',False,'log','log',False,False,'log','log','log','log','log','log','log','log','log','log',False,False,'log'],
        'yaxis': ['@SIO','#SIO','@SIO','CH3OH','#SIO','SIO','#CH3OH','#SIO','@SIO','@CH3OH','#SIO','@SIO','@CH3OH','CH3OH','SIO','@SIO','SIO','#CH3OH','@CH3OH','SIO'],
        'ylog': ['log','log',False,'log','log',False,'log','log','log',False,'log','log','log',False,'log','log','log','log','log','log']
    },
    constants.SHOCK:{}
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
    
    for logxscale, logyscale in logscales:
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
        
        fig.suptitle(tipo, size='xx-large')
        fig.savefig(figName, dpi=300, bbox_inches='tight')