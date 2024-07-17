import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import seaborn as sns
import pandas as pd
import constants, os, math

myCmap=sns.diverging_palette(170, 330, l=65, center="dark", as_cmap=True)
myRnbw=sns.blend_palette(['#72469b','#0fa4d2','#c2e000','#ca4c16','#c02321'],as_cmap=True)

# Dataframe builder
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

    campos=['runName','normalizedTime','normalizedTime_log','Time', 'Time_log']+[f'{prop}_log' for prop in physical[tipo]]+constants.initparams[tipo]
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

def checkFolders(nameBase, subFolders):
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


# Plotting
def plottingGrid(df, xaxis, yaxis, tipo, nameBase, focusList, plotType, contVar= '', cMap=''):
    checkFolders(nameBase, [plotType+'/'])

    for i, phys in enumerate(xaxis):
        fig, axs = plt.subplots(1, len(focusList), figsize=(5*len(focusList),4))
        fig.subplots_adjust(wspace=0.25,top=0.9)
        
        spec=yaxis[i]

        figName= '_'.join([nameBase+plotType+'/'+tipo.replace(' ','').upper()+contVar,plotType,phys,spec])+'.png'
        if os.path.exists(figName.replace(phys+'_'+spec,spec+'_'+phys)): continue

        for j, focus in enumerate(focusList):
            mycMap= sns.hls_palette(s=1, l=.4, h=j*.17, n_colors=len(df[focus].unique())) if cMap == '' else cMap
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
            if spec in constants.species+[s+'_log' for s in constants.species]:
                ax.set_ybound(-14,-4)
                ax.minorticks_on()

        fig.suptitle(tipo.upper())
        fig.savefig(figName, dpi=300, bbox_inches='tight')
        plt.close()

def jointPlot(df, xaxis, yaxis, tipo, nameBase, focusList, contVar= '', cMap=''):
    checkFolders(nameBase, [constants.JOINT+'/'])

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
    checkFolders(nameBase, ['contVars'+'/'])

    for i, phys in enumerate(xaxis):
        spec=yaxis[i]
        for focus in focusList:
            figName= '_'.join([nameBase+'contVars'+'/'+tipo.replace(' ','').upper(),constants.SCATTER,focus,phys,spec])+'.png'
            if os.path.exists(figName.replace(phys+'_'+spec,spec+'_'+phys)): continue
            
            fig, ax = plt.subplots(figsize=(7,5))
            fig.subplots_adjust(top=0.93)
            snsax= sns.scatterplot(df,x=phys,y=spec, hue= focus, palette='hsv', linewidth=0, legend=None, alpha=0.5, s=15, ax=ax)
            if spec in constants.species+[s+'_log' for s in constants.species]:
                ax.set_ybound(-14,-4)
                ax.minorticks_on()

            norm = plt.Normalize(df[focus].min(), df[focus].max())
            sm = plt.cm.ScalarMappable(cmap="hsv", norm=norm)
            sm.set_array([])
            snsax.figure.colorbar(sm, ax=ax, label=focus)
            snsax.figure.savefig(figName, dpi=300, bbox_inches='tight')
            plt.close()

def timePhysPlot(df, propList, tipo, nameBase, plotType=constants.BAND, focus='runName'):
    checkFolders(nameBase, [plotType+'/'])

    figName= '_'.join([nameBase+plotType+'/'+tipo.replace(' ','').upper(),constants.TIME, '' if focus=='runName' else focus])+'.png'
    wd=math.ceil(len(propList)/2)
    colormap= myRnbw if focus in constants.varPhys[tipo] else 'Dark2'
        
    fig, axs = plt.subplots(2,wd, figsize=(8*wd, 6*2), sharex=True)
    fig.subplots_adjust(wspace=0.15, hspace=0)

    for i, prop in enumerate(propList):
        ax=axs[i//(wd)][i%(wd)]
        if plotType == constants.BAND:
            snsax=sns.lineplot(df, x='normalizedTime_log', y=prop, ax=ax, 
                            hue=focus, palette=colormap, 
                            alpha=0.75,
                            errorbar=lambda x: (x.min(), x.max()),
                            legend='auto' if i==wd//2 and not focus=='runName' else None
                            )
        elif plotType == constants.SCATTER:
            snsax=sns.scatterplot(df, x='normalizedTime_log', y=prop, ax=ax,
                                hue=focus, palette=colormap, 
                                linewidth=0, alpha=0.75, s=15,
                                legend='auto' if i==wd//2 and not focus=='runName' else None
                                )
            
        if i==wd//2 and not focus=='runName': sns.move_legend(ax, "lower center", bbox_to_anchor=(0.5, 1), ncol=6)
        if prop in constants.species+[s+'_log' for s in constants.species]:
            ax.set_ybound(-14,-4)
            ax.minorticks_on()
    fig.suptitle(f"Time Evolution: {tipo.upper()}", size='large', y=0.95)

    fig.savefig(figName, dpi=300, bbox_inches='tight')
    plt.close()

def timeSpecPlot(df, propList, tipo, nameBase, plotType=constants.BAND, focus='runName'):
    checkFolders(nameBase, [plotType+'/'])

    figName= '_'.join([nameBase+plotType+'/'+tipo.replace(' ','').upper(),constants.TIME, '' if focus=='runName' else focus])+'.png'
    colormap= myRnbw if focus in constants.varPhys[tipo] else 'Dark2'
    cont= focus in constants.varPhys[tipo]
        
    if cont: fig, axs = plt.subplots(1,len(propList)+1, figsize=(8*len(propList), 6), width_ratios=len(propList)*[10]+[1])
    else: fig, axs = plt.subplots(1,len(propList), figsize=(8*len(propList), 6))

    fig.subplots_adjust(top=.85,wspace=0.15, hspace=0.05)
    for i, prop in enumerate(propList):
        ax=axs[i]
        snsax=sns.scatterplot(df, x='normalizedTime_log', y=prop, ax=ax,
                    hue=focus, palette=colormap, 
                    linewidth=0, alpha=0.75, s=15,
                    legend= None if i<len(propList)-1 and not cont else 'auto'
                    )
        ax.set_ybound(-14,-4)
        ax.minorticks_on()
        ax.set_title(prop)

    if cont:
        norm = plt.Normalize(df[focus].min(), df[focus].max())
        sm = plt.cm.ScalarMappable(cmap=colormap, norm=norm)
        sm.set_array([])
        snsax.figure.colorbar(sm, cax=axs[len(propList)], label=focus)
    else:
        sns.move_legend(axs[len(propList)-1], 'center left', bbox_to_anchor=(1, 0.5))

    fig.suptitle(f"Time Evolution: {tipo.upper()}", size='large', y=0.95)
    fig.savefig(figName, dpi=300, bbox_inches='tight')
    plt.close()

def typeAbundanceGrid(df, focusList, nameBase, xaxis='normalizedTime_log', xbound=-6):
    checkFolders(nameBase, [constants.ABUNDANCE+'/'])

    for focus in focusList:
        figName= '_'.join([nameBase+constants.ABUNDANCE+'/'+constants.BOTH.upper(),constants.ABUNDANCE,focus])+'.png'
        cont= focus in constants.varPhys[constants.BOTH]
        colormap= myRnbw if cont else 'Dark2'
        specList= constants.species

        fig = plt.figure(figsize=(8*len(specList), 6*2))
        if cont:
            gs = GridSpec(2, len(specList)+1, figure=fig, width_ratios=len(specList)*[10]+[1],
                          top=.9,wspace=0, hspace=0.1)
        else: 
            gs = GridSpec(2, len(specList), figure=fig,
                          top=.9,wspace=0, hspace=0.1)

        focus=focus+'_log'
        for j, tipo in enumerate([constants.HOTCORE, constants.SHOCK]):
            for i, spec in enumerate(specList):
                ax=fig.add_subplot(gs[j,i])
                snsax=sns.scatterplot(df[(df['tipo']==tipo)&(df['species']==spec+'_log')],
                                      x=xaxis, y='abundance_log', ax=ax,
                                      hue=focus, palette=colormap, 
                                      linewidth=0, alpha=0.75, s=15,
                                      legend= 'auto' if j==0 and i==len(specList)-1 and not cont else None
                                      )
                ax.set_ybound(-14,-4)
                ax.set_xbound(xbound,0.1)
                ax.minorticks_on()
                if i>0:
                    ax.set_ylabel(None)
                    ax.set_yticklabels([])
                if j<1:
                    ax.set_xlabel(None)
                    ax.set_xticklabels([])
                ax.set_title(f"type= {tipo} | species= {spec}")
                if j==0 and i==len(specList)-1 and not cont: legAx=ax

        if cont:
            cax=fig.add_subplot(gs[:, -1])
            norm = plt.Normalize(df[focus].min(), df[focus].max())
            sm = plt.cm.ScalarMappable(cmap=colormap, norm=norm)
            sm.set_array([])
            snsax.figure.colorbar(sm, cax=cax, label=focus)
        else:
            sns.move_legend(legAx, 'center left', bbox_to_anchor=(1, 0.5))

        fig.suptitle(f"Time Evolution: {tipo.upper()}", size='large', y=0.95)
        fig.savefig(figName, dpi=300, bbox_inches='tight')
        plt.close()

def typePhysicalGrid(df, physical, species, nameBase):
    checkFolders(nameBase, [constants.TIME+'/'])

    for spec in species:
        figName= '_'.join([nameBase+constants.TIME+'/'+constants.BOTH.upper(),constants.TIME,spec])+'.png'

        fig, axs = plt.subplots(2,len(physical), figsize=(8*len(physical), 12), sharex=True)
        fig.subplots_adjust(top=0.9,wspace=0.15, hspace=0)
        fig.suptitle(f"Time Evolution: {spec}", size='large')

        for i, phys in enumerate(physical):
            sns.scatterplot(df, x="normalizedTime_log", y=spec+"_log",
                            linewidth=0, alpha=0.5, ax=axs[0][i], 
                            hue='tipo', palette='hls', legend='auto' if i==math.floor(len(physical)/2) else None)
            axs[0][i].set_ybound(-14,-4)
            axs[0][i].minorticks_on()
            sns.scatterplot(df, x="normalizedTime_log", y=phys+"_log",
                            linewidth=0, alpha=0.5, ax=axs[1][i], legend=None,
                            hue='tipo', palette='hls')
            # axs[0][i].set_xlim(left=1e-7, right=1.1)
        sns.move_legend(axs[0][math.floor(len(physical)/2)], "upper center", bbox_to_anchor=(0.5, 1.15), ncol=3)
        
        fig.savefig(figName, dpi=300, bbox_inches='tight')
        plt.close()

def abundanceScater(df, xaxis, focus, nameBase, tipo=constants.BOTH, cols=[constants.HOTCORE, constants.SHOCK], col_filter='tipo'):
    checkFolders(nameBase, [constants.ABUNDANCE+'/'])
    figName= '_'.join([nameBase+constants.ABUNDANCE+'/'+tipo,constants.SCATTER,focus,xaxis,constants.ABUNDANCE])+'.png'

    fig, axs = plt.subplots(1,len(cols), figsize=(7*len(cols),7))
    for i, col in enumerate(cols):
        ax=axs[i]

        sns.scatterplot(df[df[col_filter]==col],
                        x=xaxis,y='abundance_log', ax=ax,
                        hue= focus, palette='hsv',
                        linewidth=0, alpha=0.5, s=10)
        ax.set_ybound(-14,-4)
        ax.minorticks_on()
        ax.set_title(col.upper())
        sns.move_legend(ax, "upper center", bbox_to_anchor=(0.5, -0.1), ncols=4)
    
    fig.savefig(figName, dpi=300, bbox_inches='tight')
    plt.close()

def localAbundancePlot(df, phys, tipo, nameBase, momento=constants.FINAL):
    checkFolders(nameBase, ['/'])

    figName= '_'.join([nameBase+'/'+tipo.replace(' ','').upper(),constants.ABUNDANCE, momento, phys])+'.png'
    
    fig, ax = plt.subplots(figsize=(7,7))
    fig.subplots_adjust(top=0.95)
    sns.scatterplot(df, x=phys, y='abundance_log',
                hue='species', palette='nipy_spectral',
                linewidth=0, ax=ax, alpha=0.5,
                )
    sns.move_legend(ax, "upper right", bbox_to_anchor=(1, -0.07), ncol=4)
    ax.set_ybound(-14,-4)
    ax.minorticks_on()
    fig.suptitle(tipo.upper()+f': {momento} Abundances')
    ax.annotate(df.groupby(by=['species'])['abundance_log'].count(), xy=(0,0), xycoords='figure fraction', va='bottom', ha='left')

    fig.savefig(figName, dpi=300, bbox_inches='tight')
    plt.close()