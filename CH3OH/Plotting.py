import numpy as np
import matplotlib.pyplot as plt, matplotlib.colors as colors
from matplotlib.gridspec import GridSpec
import seaborn as sns
import pandas as pd
import constants, os, math

# 7668b6-2e82dc-7c8e67-e6b40f-e26628-8c001a
myCmap=sns.diverging_palette(170, 330, l=65, center="dark", as_cmap=True)

# Dataframe builder
def buildDataframe(tipos, folder, physical, species, singleDf=True):
    if singleDf: tipos=[tipos]
    else: dflist=[]
    
    for tipo in tipos:
        df= pd.read_csv(folder.format(tipo)+'.csv', index_col=0)

        df = df.loc[:,['Time']+physical[tipo]+species+['runName']]
        df[species] = df[species][df[species] >= 1e-14]

        if tipo==constants.HOTCORE:
            max_size_df = df.loc[df.groupby('runName')['CH3OH'].idxmax()]
            merged_df = df.merge(max_size_df[['runName', 'Time']], on='runName', suffixes=('', '_max_size'))
            df = merged_df[merged_df['Time'] <= merged_df['Time_max_size']].drop(columns='Time_max_size')

        for prop in ['Time']+physical[tipo]+species:
            with np.errstate(divide='ignore'): df[f'{prop}_log']=np.log10(df[prop])
        
        df=df.reset_index().drop(columns=['index'])
        df=df.join(pd.DataFrame(df['runName'].str.replace('.dat','').str.split('_').values.tolist(),
                                columns=constants.initparams[tipo]), rsuffix='_str')
        df['normalizedTime']= df['Time']/df.groupby('runName')['Time'].transform('max')
        with np.errstate(divide='ignore'): df['normalizedTime_log']= np.log10(df['normalizedTime'])

        if singleDf:
            return df
        else:
            df['tipo']=tipo
            dflist.append(df.copy())
    
    return pd.concat(dflist, ignore_index=True)

def localAbundanceDataframe(df, species, physical, tipo, momento=constants.FINAL, singleDf=True):
    if momento == constants.FINAL:
        dfFinal=df.loc[df['normalizedTime'] == 1]
    elif momento == constants.TMAX:
        dfFinal=df.loc[df['gasTemp'] == df.groupby('runName')['gasTemp'].transform('max')]
    elif momento == constants.SHOCKAVG:
        vals=['normalizedTime','Time']+physical[tipo]+species
        dfFinal=df.loc[df['gasTemp'] > 15].groupby(['runName']+constants.initparams[tipo],as_index=False)[vals].mean()
        for prop in vals:
            with np.errstate(divide='ignore'): dfFinal[f'{prop}_log']=np.log10(dfFinal[prop])
    elif momento == constants.ALL:
        dfFinal=df

    campos=['runName','normalizedTime','normalizedTime_log','Time', 'Time_log']+[f'{prop}_log' for prop in physical[tipo]]+constants.initparams[tipo]+physical[tipo]
    if not singleDf: campos.append('tipo')
    campos=list(set(campos))

    tDic=dict([(key, []) for key in campos+['abundance','abundance_log', 'species']])
    for i in dfFinal.index:
        for spec in species:
            tDic['abundance'].append(dfFinal.at[i,spec]) 
            with np.errstate(divide='ignore'): tDic['abundance_log'].append(np.log10(dfFinal.at[i,spec]))
            tDic['species'].append(spec)
            for c in campos:
                tDic[c].append(dfFinal.at[i,c])
    return pd.DataFrame(tDic)

def checkFolders(nameBase, subFolders=['']):
    for subF in subFolders:
        if not os.path.exists(nameBase+subF): os.makedirs(nameBase+subF)

# Correlation Matrix
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

def corrGrid(df, xaxis, yaxis, tipo: str, barrera=0, saveFig=False, nameBase=''):
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
    if saveFig:
        checkFolders(nameBase)
        fig.savefig('_'.join([nameBase+tipo.replace(' ','').upper(),'focusedCorrGrid'])+'.png',
                    dpi=300, bbox_inches='tight')
    return cor

# Plotting
def singleScatter(df, xaxis, yaxis, focus, tipo, nameBase, title,
                  xbound=-6, saveFig=True, returnAx=False, figAx=None):
    checkFolders(nameBase)
    figName= '_'.join([nameBase+tipo.replace(' ','').upper(),xaxis,yaxis,focus])+'.png'

    contVar= focus in constants.varPhys[tipo]
    colorPalette=sns.blend_palette(['#2e82dc','#5d417b','#8c001a','#f2c32c'],as_cmap=True) if contVar else ['#72469b','#0fa4d2','#c2e000','#ca4c16','#c02321'][:df[focus].nunique()]
    norm = colors.LogNorm(df[focus].min(),df[focus].max())if contVar else None

    fig, axi = plt.subplots(figsize=(10 if contVar else 8,8))
    axs= figAx if returnAx else axi
    fig.subplots_adjust(top=0.95)
    sns.scatterplot(df, x=xaxis+'_log', y=yaxis+'_log',
                    hue=focus, palette=colorPalette, hue_norm=norm,
                    legend=None if contVar else 'auto',
                    linewidth=0, alpha=0.75, s=15, ax=axs)
    axs.minorticks_on()

    if xaxis == 'normalizedTime': axs.set_xbound(xbound,0.1)
    if yaxis in constants.species+['abundance']: axs.set_ybound(-14,-4)

    if contVar:
        sm = plt.cm.ScalarMappable(cmap=colorPalette, norm=norm)
        sm.set_array([])
        fig.colorbar(sm, ax=axs, label=focus)
    else:
        sns.move_legend(axs, "upper center", bbox_to_anchor=(0.5, -0.1), ncol=df[focus].nunique())

    fig.suptitle(title)
    if saveFig: fig.savefig(figName, dpi=300, bbox_inches='tight')
    plt.close()

def gridScatter(df, plotDict, tipo, title, nameBase, xbound=-6, saveFig=True):
    checkFolders(nameBase)
    figName= '_'.join([nameBase+tipo.replace(' ','').upper()]+['_'.join(plotDict[row]) for row in plotDict])+'.png'

    cols, rows, focusList = (plotDict[row] for row in plotDict)
    nRow=len(rows)
    nCol=len(cols)

    fig, axs = plt.subplots(nRow, nCol, figsize=(8*nCol,6*nRow))
    fig.subplots_adjust(top=0.95, wspace=0.15, hspace=0.3)
    fig.suptitle(title, size='xx-large', y=1)

    for i in range(nRow):
        for j in range(nCol):
            if nRow>1 and nCol>1: ax=axs[i][j]
            elif nRow>1: ax=axs[i]
            else: ax=axs[j]

            singleScatter(df, cols[j], rows[i], focusList[j], tipo, nameBase, '', xbound=xbound, saveFig=False, returnAx=True, figAx=ax)
            ax.set_title(' | '.join([cols[j], rows[i], focusList[j]]))

    if saveFig: fig.savefig(figName, dpi=300, bbox_inches='tight')
    plt.close()

def singleBox(df, xaxis, yaxis, focus, tipo, nameBase, title,
                  saveFig=True, returnAx=False, figAx=None):
    checkFolders(nameBase)
    figName= '_'.join([nameBase+tipo.replace(' ','').upper(),xaxis,yaxis,focus])+'.png'

    notLeg= False if focus else True
    if notLeg: focus = xaxis

    fig, axi = plt.subplots(figsize=(10,8))
    axs= figAx if returnAx else axi
    fig.subplots_adjust(top=0.95)
    sns.boxplot(df, x=xaxis, y=yaxis,
                hue=focus, palette='hls',
                legend=None if notLeg else 'auto',
                orient='v', log_scale=True, ax=axs)

    if yaxis in constants.species+['abundance']: axs.set_ybound(1e-14,1e-4)
    if not notLeg: sns.move_legend(axs, "upper center", bbox_to_anchor=(0.5, -0.1), ncol=df[focus].nunique())

    fig.suptitle(title)
    if saveFig: fig.savefig(figName, dpi=300, bbox_inches='tight')
    plt.close()

def gridBox(df, plotDict, tipo, title, nameBase, saveFig=True):
    checkFolders(nameBase)
    figName= '_'.join([nameBase+tipo.replace(' ','').upper()]+['_'.join(plotDict[row]) for row in plotDict])+'.png'

    cols, rows, focusList = (plotDict[row] for row in plotDict)
    nRow=len(rows)
    nCol=len(cols)

    fig, axs = plt.subplots(nRow, nCol, figsize=(8*nCol,6*nRow))
    fig.subplots_adjust(top=0.95, wspace=0.15, hspace=0.3)
    fig.suptitle(title, size='xx-large', y=1)

    for i in range(nRow):
        for j in range(nCol):
            if nRow>1 and nCol>1: ax=axs[i][j]
            elif nRow>1: ax=axs[i]
            else: ax=axs[j]

            singleBox(df, cols[j], rows[i], focusList[j], tipo, nameBase, '', saveFig=False, returnAx=True, figAx=ax)
            ax.set_title(' | '.join([cols[j], rows[i], focusList[j]]))

    if saveFig: fig.savefig(figName, dpi=300, bbox_inches='tight')
    plt.close()