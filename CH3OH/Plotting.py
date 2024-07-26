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
            max_meth_df = df.loc[df.groupby('runName')['CH3OH'].idxmax()]
            merged_df = df.merge(max_meth_df[['runName', 'Time']], on='runName', suffixes=('', '_max_meth'))
            min_ftemp_df = df.loc[df.groupby('runName')['gasTemp'].idxmax()]
            merged_df = merged_df.merge(min_ftemp_df[['runName', 'Time']], on='runName', suffixes=('', '_min_ftemp'))
            df = merged_df[merged_df['Time'] <= merged_df[['Time_max_meth','Time_min_ftemp']].max(axis=1)].drop(columns=['Time_max_meth','Time_min_ftemp'])

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
def abundanceComparison(la_df, focusList, hueList, nameBase, saveFig=True, returnFilepaths=False, onlyDF=False):
    if returnFilepaths: pathDic=[]
    for focus in focusList:
        for param in la_df[focus].unique():
            df=la_df[la_df[focus]==param]
            for hue in [h for h in hueList if h!=focus]:
                checkFolders(nameBase)
                # figName='_'.join([nameBase+constants.ABUNDANCE,focus,param,hue])+'.png'
                figName='_'.join([nameBase+constants.ABUNDANCE,constants.SCATTER,focus,param,hue])+'.png'
                if returnFilepaths:pathDic.append({'focus':focus,'param':param,'hue':hue,'path':figName})
                if onlyDF: continue

                fig, ax = plt.subplots(figsize=(20,10), layout='tight')
                ax.grid(True)  
                # sns.lineplot(data=df, x='Time', y='abundance',
                sns.scatterplot(data=df, x='Time', y='abundance',
                            hue=hue, style='tipo',
                            palette='gnuplot',
                            linewidth=0, s=50, markers={constants.HOTCORE: "d", constants.SHOCK: "P"},
                            # errorbar=lambda x: (x.min(), x.max()),
                            ax=ax)
                ax.set_xscale('log')
                ax.set_yscale('log')
                ax.set_xbound(1,df['Time'].max())
                ax.set_ybound(1e-14,1e-4)
                sns.move_legend(ax, "upper center", bbox_to_anchor=(0.5, -0.06), ncol=3 if hue==constants.IDENS else 2)
                fig.suptitle('CH3OH Abundance - Time Evolution Comparison \n'+' | '.join([f'{focus}={param}',hue]))
                if saveFig: fig.savefig(figName, dpi=300, bbox_inches='tight')
                plt.close()
    if returnFilepaths: return pd.DataFrame(pathDic)

def abundanceComparisonGrid(imList, ncols, nrows, focusParm, nameBase, saveFig=True, title='CH3OH Abundance Comparison '):
    checkFolders(nameBase)
    # figName= '_'.join([nameBase+constants.ABUNDANCE,focusParm])+'.png'
    figName= '_'.join([nameBase+constants.ABUNDANCE,constants.SCATTER,focusParm])+'.png'

    fig, axs = plt.subplots(ncols,nrows, figsize=(6*nrows,3*ncols))
    fig.subplots_adjust(top=0.95, hspace=0, wspace=0)

    for i, image_file in enumerate(imList):
        ax=axs[i//nrows][i%nrows]
        image = plt.imread(image_file)
        ax.imshow(image)
        ax.axis('off')
    
    fig.suptitle(title+focusParm.upper())
    if saveFig: fig.savefig(figName, dpi=300, bbox_inches='tight')
    plt.close()

def continuityPlot(df, runN, species, tipo, nameBase, saveFig=True):
    checkFolders(nameBase)
    figName= '_'.join([nameBase+tipo.replace(' ','').upper(),constants.CONTINUITY,runN.strip('.dat')])+'.png'
    
    tdf=df[df['runName']==runN]
    methmax=tdf[tdf['CH3OH']==tdf['CH3OH'].max()]['Time_log'].max()
    ftmin=tdf[tdf['gasTemp']==tdf['gasTemp'].max()]['Time_log'].min()

    fig, axs = plt.subplots(2, 1, figsize=(6,8), sharex=True)
    fig.subplots_adjust(top=0.95, hspace=0.05)

    for i,col in enumerate(['gasTemp', 'Density', 'av']):
        axs[1].plot(tdf['Time_log'], tdf[col], label=col, c=['#ca1551','#1f7a8c','#884ab2'][i])
        
    fig.suptitle(runN)
    axs[1].axvline(ftmin, c='blue')
    axs[1].axvline(methmax, c='red')
    axs[1].set_yscale('log')
    axs[1].set_xlabel('Time_log')
    axs[1].grid(True)  

    for j,col in enumerate(species):
        axs[0].plot(tdf['Time_log'], tdf[col], label=col, c=['#4cb944','#e76f51'][j])
    axs[0].axvline(methmax, c='red')
    axs[0].axvline(ftmin, c='blue')
    axs[0].set_yscale('log')
    axs[0].set_ybound(1e-14,1e-4)
    axs[0].grid(True)  

    fig.legend(ncols=3+len(species), loc='lower center')
    if saveFig: fig.savefig(figName, dpi=300, bbox_inches='tight')
    plt.close()

def continuityGrid(imList, tipo, nameBase, saveFig=True):
    checkFolders(nameBase)
    figName= '_'.join([nameBase+tipo.replace(' ','').upper(),constants.CONTINUITY])+'.png'

    fig, axs = plt.subplots(4,9, figsize=(32,16))
    fig.subplots_adjust(top=0.95, hspace=0, wspace=0)

    for i, image_file in enumerate(imList):
        ax=axs[i//9][i%9]
        image = plt.imread(image_file)
        ax.imshow(image)
        ax.axis('off')
    
    fig.suptitle('Continuity Plot '+tipo.upper())
    if saveFig: fig.savefig(figName, dpi=300, bbox_inches='tight')
    plt.close()

def localAbundancePlot(m_df, focus, tipo, nameBase, returnFilepaths=False):
    checkFolders(nameBase)
    colorPalette=['#f72585','#2667ff','#004b23']
    markers=['d','s','o']
    filePaths=[]

    for param in m_df[focus].unique():
        dfi=m_df[m_df[focus]==param]
        figName= '_'.join([nameBase+tipo.replace(' ','').upper(),'abundance',focus,str(param)])+'.png'

        fig, axs = plt.subplots(figsize=(16,8))
        fig.subplots_adjust(top=0.95)
        for i, time in enumerate(constants.times[tipo]):
            df=localAbundanceDataframe(dfi, constants.species, constants.physical, tipo, momento=time, singleDf=True)
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

def localAbundanceGrid(imList, tipo, focus, nameBase, saveFig=True):
    checkFolders(nameBase)
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

colorDict= {'10.0_3.0_1000.0_10.0.dat': np.array([0.32020328, 0.67884678, 0.60502316, 1.]),
 '10.0_3.0_1000.0_25.0.dat': np.array([0.31589148, 0.66636952, 0.59420602, 1.]),
 '10.0_3.0_1000.0_40.0.dat': np.array([0.31014241, 0.64973317, 0.57978317, 1.]),
 '10.0_1000.0_1000.0_10.0.dat': np.array([0.30583061, 0.63725592, 0.56896603, 1.]),
 '10.0_1000.0_1000.0_25.0.dat': np.array([0.30008155, 0.62061957, 0.55454319, 1.]),
 '10.0_1000.0_1000.0_40.0.dat': np.array([0.29433248, 0.60398322, 0.54012034, 1.]),
 '1000.0_3.0_1000.0_10.0.dat': np.array([0.29002068, 0.59150597, 0.5293032 , 1.]),
 '1000.0_3.0_1000.0_25.0.dat': np.array([0.28427161, 0.57486962, 0.51488035, 1.]),
 '1000.0_3.0_1000.0_40.0.dat': np.array([0.27995981, 0.56239236, 0.50406321, 1.]),
 '1000.0_1000.0_1000.0_10.0.dat': np.array([0.27421074, 0.54575602, 0.48964036, 1.]),
 '1000.0_1000.0_1000.0_25.0.dat': np.array([0.26846167, 0.52911967, 0.47521752, 1.]),
 '1000.0_1000.0_1000.0_40.0.dat': np.array([0.26414987, 0.51664241, 0.46440038, 1.]),
 '10.0_3.0_10000.0_10.0.dat': np.array([0.25840081, 0.50000607, 0.44997753, 1.]),
 '10.0_3.0_10000.0_25.0.dat': np.array([0.25408901, 0.48752881, 0.43916039, 1.]),
 '10.0_3.0_10000.0_40.0.dat': np.array([0.24833994, 0.47089246, 0.42473754, 1.]),
 '10.0_1000.0_10000.0_10.0.dat': np.array([0.24259087, 0.45425612, 0.4103147 , 1.]),
 '10.0_1000.0_10000.0_25.0.dat': np.array([0.23827907, 0.44177886, 0.39949756, 1.]),
 '10.0_1000.0_10000.0_40.0.dat': np.array([0.23253   , 0.42514251, 0.38507471, 1.]),
 '1000.0_3.0_10000.0_10.0.dat': np.array([0.22750237, 0.41059383, 0.37246176, 1.]),
 '1000.0_3.0_10000.0_25.0.dat': np.array([0.22175331, 0.39395749, 0.35803891, 1.]),
 '1000.0_3.0_10000.0_40.0.dat': np.array([0.21600424, 0.37732114, 0.34361606, 1.]),
 '1000.0_1000.0_10000.0_10.0.dat': np.array([0.21169244, 0.36484388, 0.33279892, 1.]),
 '1000.0_1000.0_10000.0_25.0.dat': np.array([0.20594337, 0.34820754, 0.31837608, 1.]),
 '1000.0_1000.0_10000.0_40.0.dat': np.array([0.20163157, 0.33573028, 0.30755894, 1.]),
 '10.0_3.0_100000.0_10.0.dat': np.array([0.1958825 , 0.31909393, 0.29313609, 1.]),
 '10.0_3.0_100000.0_25.0.dat': np.array([0.19013344, 0.30245759, 0.27871324, 1.]),
 '10.0_3.0_100000.0_40.0.dat': np.array([0.18582163, 0.28998033, 0.2678961 , 1.]),
 '10.0_1000.0_100000.0_10.0.dat': np.array([0.18007257, 0.27334398, 0.25347325, 1.]),
 '10.0_1000.0_100000.0_25.0.dat': np.array([0.17576077, 0.26086673, 0.24265612, 1.]),
 '10.0_1000.0_100000.0_40.0.dat': np.array([0.1700117 , 0.24423038, 0.22823327, 1.]),
 '1000.0_3.0_100000.0_10.0.dat': np.array([0.16426263, 0.22759403, 0.21381042, 1.]),
 '1000.0_3.0_100000.0_25.0.dat': np.array([0.15995083, 0.21511678, 0.20299328, 1.]),
 '1000.0_3.0_100000.0_40.0.dat': np.array([0.15420176, 0.19848043, 0.18857043, 1.]),
 '1000.0_1000.0_100000.0_10.0.dat': np.array([0.14988996, 0.18600317, 0.1777533 , 1.]),
 '1000.0_1000.0_100000.0_25.0.dat': np.array([0.14414089, 0.16936683, 0.16333045, 1.]),
 '1000.0_1000.0_100000.0_40.0.dat': np.array([0.13839183, 0.15273048, 0.1489076 , 1.]),
 '10.0_3.0_1000000.0_50.0.dat': np.array([0.17250735, 0.14082819, 0.15919272, 1.]),
 '10.0_3.0_1000000.0_100.0.dat': np.array([0.19599123, 0.15093827, 0.17805552, 1.]),
 '10.0_3.0_1000000.0_300.0.dat': np.array([0.21947511, 0.16104836, 0.19691831, 1.]),
 '10.0_1000.0_1000000.0_50.0.dat': np.array([0.23708802, 0.16863092, 0.21106541, 1.]),
 '10.0_1000.0_1000000.0_100.0.dat': np.array([0.2605719 , 0.17874101, 0.22992821, 1.]),
 '10.0_1000.0_1000000.0_300.0.dat': np.array([0.27818481, 0.18632357, 0.2440753 , 1.]),
 '1000.0_3.0_1000000.0_50.0.dat': np.array([0.30166869, 0.19643365, 0.2629381 , 1.]),
 '1000.0_3.0_1000000.0_100.0.dat': np.array([0.32515257, 0.20654374, 0.28180089, 1.]),
 '1000.0_3.0_1000000.0_300.0.dat': np.array([0.34276548, 0.2141263 , 0.29594799, 1.]),
 '1000.0_1000.0_1000000.0_50.0.dat': np.array([0.36624937, 0.22423639, 0.31481079, 1.]),
 '1000.0_1000.0_1000000.0_100.0.dat': np.array([0.38386228, 0.23181895, 0.32895788, 1.]),
 '1000.0_1000.0_1000000.0_300.0.dat': np.array([0.40734616, 0.24192904, 0.34782068, 1.]),
 '10.0_3.0_10000000.0_50.0.dat': np.array([0.43083004, 0.25203912, 0.36668348, 1.]),
 '10.0_3.0_10000000.0_100.0.dat': np.array([0.44844295, 0.25962168, 0.38083057, 1.]),
 '10.0_3.0_10000000.0_300.0.dat': np.array([0.47192683, 0.26973177, 0.39969337, 1.]),
 '10.0_1000.0_10000000.0_50.0.dat': np.array([0.48953974, 0.27731433, 0.41384047, 1.]),
 '10.0_1000.0_10000000.0_100.0.dat': np.array([0.51302362, 0.28742442, 0.43270326, 1.]),
 '10.0_1000.0_10000000.0_300.0.dat': np.array([0.5365075 , 0.2975345 , 0.45156606, 1.]),
 '1000.0_3.0_10000000.0_50.0.dat': np.array([0.55704443, 0.30637589, 0.46806179, 1.]),
 '1000.0_3.0_10000000.0_100.0.dat': np.array([0.58052832, 0.31648597, 0.48692459, 1.]),
 '1000.0_3.0_10000000.0_300.0.dat': np.array([0.59814123, 0.32406854, 0.50107169, 1.]),
 '1000.0_1000.0_10000000.0_50.0.dat': np.array([0.62162511, 0.33417862, 0.51993448, 1.]),
 '1000.0_1000.0_10000000.0_100.0.dat': np.array([0.64510899, 0.34428871, 0.53879728, 1.]),
 '1000.0_1000.0_10000000.0_300.0.dat': np.array([0.6627219 , 0.35187127, 0.55294437, 1.]),
 '10.0_3.0_100000000.0_50.0.dat': np.array([0.68620578, 0.36198135, 0.57180717, 1.]),
 '10.0_3.0_100000000.0_100.0.dat': np.array([0.70381869, 0.36956392, 0.58595427, 1.]),
 '10.0_3.0_100000000.0_300.0.dat': np.array([0.72730257, 0.379674  , 0.60481706, 1.]),
 '10.0_1000.0_100000000.0_50.0.dat': np.array([0.75078645, 0.38978409, 0.62367986, 1.]),
 '10.0_1000.0_100000000.0_100.0.dat': np.array([0.76839937, 0.39736665, 0.63782695, 1.]),
 '10.0_1000.0_100000000.0_300.0.dat': np.array([0.79188325, 0.40747674, 0.65668975, 1.]),
 '1000.0_3.0_100000000.0_50.0.dat': np.array([0.80949616, 0.4150593 , 0.67083685, 1.]),
 '1000.0_3.0_100000000.0_100.0.dat': np.array([0.83298004, 0.42516938, 0.68969964, 1.]),
 '1000.0_3.0_100000000.0_300.0.dat': np.array([0.85646392, 0.43527947, 0.70856244, 1.]),
 '1000.0_1000.0_100000000.0_50.0.dat': np.array([0.87407683, 0.44286203, 0.72270954, 1.]),
 '1000.0_1000.0_100000000.0_100.0.dat': np.array([0.89756071, 0.45297212, 0.74157233, 1.]),
 '1000.0_1000.0_100000000.0_300.0.dat': np.array([0.91517362, 0.46055468, 0.75571943, 1.])}