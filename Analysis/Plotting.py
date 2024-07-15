import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import constants, os, math

myCmap=sns.diverging_palette(170, 330, l=65, center="dark", as_cmap=True)
myRnbw=sns.blend_palette(['#72469b','#0fa4d2','#c2e000','#ca4c16','#c02321'],as_cmap=True)

def buildDataframe(tipos, folder, physical, species, singleDf=True):
    if singleDf: tipos=[tipos]
    else: dflist=[]
    
    for tipo in tipos:
        df= pd.read_csv(folder.format(tipo)+'.csv', index_col=0)

        df = df.loc[:,['Time']+physical[tipo]+species+['runName']]
        df[species] = df[species][df[species] >= 1e-14]

        for prop in ['Time']+physical[tipo]+species:
            with np.errstate(divide='ignore'): df[f'{prop}_log']=np.log10(df[prop])
        
        df=df.reset_index().drop(columns=['index'])
        df=df.join(pd.DataFrame(df['runName'].str.replace('.dat','').str.split('_').values.tolist(),
                                columns=constants.initparams[tipo]), rsuffix='_str')
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
        dfFinal=df.loc[df['gasTemp'] > 15].groupby(['runName']+constants.initparams[tipo],as_index=False)[['normalizedTime']+physical[tipo]+species].mean()
        for prop in physical[tipo]+species:
            with np.errstate(divide='ignore'): dfFinal[f'{prop}_log']=np.log10(dfFinal[prop])
    elif momento == constants.ALL:
        dfFinal=df

    campos=['runName','normalizedTime','Time']+[f'{prop}_log' for prop in physical[tipo]]+constants.initparams[tipo]
    if not singleDf: campos.append('tipo')
    especies=[prop+'_log' for prop in species]

    tDic=dict([(key, []) for key in campos+['abundance_log', 'species']])
    for i in dfFinal.index:
        for spec in especies:
            tDic['abundance_log'].append(dfFinal.at[i,spec]) 
            tDic['species'].append(spec)
            for c in campos:
                tDic[c].append(dfFinal.at[i,c])
    return pd.DataFrame(tDic)


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

def plottingGrid(df, xaxis, yaxis, tipo, nameBase, focusList, plotType, contVar= '', cMap=''):
    for i, phys in enumerate(xaxis):
        fig, axs = plt.subplots(1, len(focusList), figsize=(5*len(focusList),4))
        fig.subplots_adjust(wspace=0.25,top=0.9)
        
        spec=yaxis[i]

        figName= '_'.join([nameBase+plotType+'/'+tipo.replace(' ','').upper()+contVar,plotType,phys,spec])+'.png'
        if os.path.exists(figName.replace(phys+'_'+spec,spec+'_'+phys)): continue

        for j, focus in enumerate(focusList):
            mycMap= sns.hls_palette(s=1, l=.4, h=j*.17, n_colors=3) if cMap == '' else cMap
            ax= axs[j] if len(focusList)>1 else axs
            if plotType == constants.SCATTER:
                sns.scatterplot(df,x=phys,y=spec, ax=ax,
                                hue= focus, palette=mycMap,
                                linewidth=0, legend='full',
                                alpha=0.5, s=15
                                )
            elif plotType == constants.BAND:
                sns.lineplot(data=df, x=phys,y=spec, ax=ax,
                             hue= focus, palette=mycMap,
                             errorbar=lambda x: (x.min(), x.max()),
                             )
            sns.move_legend(ax, "upper center", bbox_to_anchor=(0.5, -0.15), ncol=3)

        fig.suptitle(tipo.upper())
        fig.savefig(figName, dpi=300, bbox_inches='tight')
        plt.close()

def jointPlot(df, xaxis, yaxis, tipo, nameBase, focusList, contVar= '', cMap=''):
    for i, phys in enumerate(xaxis):
        spec=yaxis[i]

        for j, focus in enumerate(focusList):
            mycMap= sns.hls_palette(s=1, l=.4, h=j*.17, n_colors=3) if cMap == '' else cMap
            figName= '_'.join([nameBase+constants.JOINT+'/'+tipo.replace(' ','').upper()+contVar,constants.JOINT,focus,phys,spec])+'.png'
            if os.path.exists(figName.replace(phys+'_'+spec,spec+'_'+phys)): continue

            f = sns.jointplot(df, x=spec,y=phys,
                            hue=focus, palette= mycMap,
                            alpha=0.5, linewidth=0,
                            )
            f.plot_marginals(sns.histplot, alpha=0.5)
            sns.move_legend(f.figure.axes[0], "upper center", bbox_to_anchor=(0.5, -0.15), ncol=3)
            
            f.savefig(figName, dpi=300, bbox_inches='tight')
        plt.close()

def contScatterPlot(df, xaxis, yaxis, tipo, nameBase, focusList):
    for i, phys in enumerate(xaxis):
        spec=yaxis[i]
        for focus in focusList:
            figName= '_'.join([nameBase+'contVars'+'/'+tipo.replace(' ','').upper(),constants.SCATTER,focus,phys,spec])+'.png'
            if os.path.exists(figName.replace(phys+'_'+spec,spec+'_'+phys)): continue
            
            fig, ax = plt.subplots(figsize=(7,5))
            fig.subplots_adjust(top=0.93)
            snsax= sns.scatterplot(df,x=phys,y=spec, hue= focus, palette='hsv', linewidth=0, legend=None, alpha=0.5, s=15, ax=ax)

            norm = plt.Normalize(df[focus].min(), df[focus].max())
            sm = plt.cm.ScalarMappable(cmap="hsv", norm=norm)
            sm.set_array([])
            snsax.figure.colorbar(sm, ax=ax, label=focus)
            snsax.figure.savefig(figName, dpi=300, bbox_inches='tight')
            plt.close()


def timePlot(df, propList, tipo, nameBase, plotType=constants.BAND, focus='runName'):
    figName= '_'.join([nameBase+plotType+'/'+tipo.replace(' ','').upper(),constants.TIME, '' if focus=='runName' else focus])+'.png'
    wd=math.ceil(len(propList)/2)
        
    fig, axs = plt.subplots(2,wd, figsize=(8*wd, 6*2), sharex=True)
    fig.subplots_adjust(wspace=0.15, hspace=0)

    for i, prop in enumerate(propList):
        ax=axs[i//(wd)][i%(wd)]
        if plotType == constants.BAND:
            sns.lineplot(df, x='normalizedTime', y=prop, ax=ax, 
                            hue=focus, palette='icefire', alpha=0.5,
                            errorbar=lambda x: (x.min(), x.max()),
                            legend='auto' if i==wd//2 else None
                            )
        elif plotType == constants.SCATTER:
            sns.scatterplot(df, x='normalizedTime', y=prop, ax=ax,
                                hue=focus, palette='icefire', 
                                linewidth=0, alpha=0.5, s=15,
                                legend='auto' if i==wd//2 else None
                                )
            
        if i==wd//2: sns.move_legend(ax, "lower center", bbox_to_anchor=(0.5, 1), ncol=6)
        ax.set_xscale('log')
        ax.set_xlim(right=1.1)
    fig.suptitle(f"Time Evolution: {tipo.upper()}", size='large', y=1.05 if focus=='runName' else 0.95)

    fig.savefig(figName, dpi=300, bbox_inches='tight')
    plt.close()

def typeAbundanceGrid(df, focusList, nameBase):
    for focus in focusList:
        figName= '_'.join([nameBase+constants.ABUNDANCE+'/'+constants.BOTH.upper(),constants.ABUNDANCE,focus])+'.png'
        
        g = sns.relplot(df, x="normalizedTime", y="abundance_log",
                        linewidth=0, alpha=0.75,
                        hue=focus+'_log', palette=myRnbw,
                        row="tipo",  col="species", row_order=[constants.SHOCK,constants.HOTCORE],
                        )
        g.set(xscale='log', xlim=(None,1.1))
        g.figure.suptitle('Abundances Timeline', size='xx-large')
        g.figure.subplots_adjust(top=0.91)
        g.savefig(figName, dpi=300, bbox_inches='tight')
        plt.close()

def typePhysicalGrid(df, physical, species, nameBase):
    for spec in species:
        figName= '_'.join([nameBase+constants.TIME+'/'+constants.BOTH.upper(),constants.TIME,spec])+'.png'

        fig, axs = plt.subplots(2,len(physical), figsize=(8*len(physical), 12), sharex=True)
        fig.subplots_adjust(top=0.9,wspace=0.15, hspace=0)
        fig.suptitle(f"Time Evolution: {spec}", size='large')

        for i, phys in enumerate(physical):
            sns.scatterplot(df, x="normalizedTime", y=spec+"_log",
                            linewidth=0, alpha=0.5, ax=axs[0][i], 
                            hue='tipo', palette='hls', legend='auto' if i==math.floor(len(physical)/2) else None)
            sns.scatterplot(df, x="normalizedTime", y=phys+"_log",
                            linewidth=0, alpha=0.5, ax=axs[1][i], legend=None,
                            hue='tipo', palette='hls')
            axs[0][i].set_xscale('log')
            axs[0][i].set_xlim(left=1e-7, right=1.1)
        sns.move_legend(axs[0][math.floor(len(physical)/2)], "upper center", bbox_to_anchor=(0.5, 1.15), ncol=3)
        
        fig.savefig(figName, dpi=300, bbox_inches='tight')
        plt.close()

def localAbundancePlot(df, phys, tipo, nameBase, momento=constants.FINAL):
    figName= '_'.join([nameBase+'/'+tipo.replace(' ','').upper(),constants.ABUNDANCE, momento, phys])+'.png'
    
    fig, ax = plt.subplots(figsize=(7,5))
    fig.subplots_adjust(top=0.93)
    sns.scatterplot(df, x=phys, y='abundance_log',
                hue='species', palette='gist_ncar',
                linewidth=0, ax=ax, alpha=0.5,
                )
    sns.move_legend(ax, "upper center", bbox_to_anchor=(0.5, -0.15), ncol=4)
    fig.suptitle(tipo.upper()+f': {momento} Abundances')

    fig.savefig(figName, dpi=300, bbox_inches='tight')
    plt.close()