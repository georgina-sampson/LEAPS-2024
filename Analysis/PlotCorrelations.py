import constants, Plotting
import matplotlib.pyplot as plt

# folder = '{}'
folder = constants.folder
nameBase= folder.format('CorrelationPlots/')

physical = constants.physical
species= constants.species


for singleAxis in [True, False]:
    print('singleAxis',singleAxis)
    subf= '/species/' if singleAxis else '/physical/'
    for tipo in [constants.HOTCORE, constants.SHOCK]:
        print(tipo)
        df= Plotting.buildDataframe(tipo, folder, physical, species)
        
        yaxis= [f'{prop}_log' for prop in species]
        if singleAxis: xaxis=yaxis
        else: xaxis= [f'{prop}_log' for prop in physical[tipo]]

        figName=nameBase+subf+tipo.replace(' ','').upper()+f"_{'species_' if singleAxis else ''}CorrGrid_log_log.png"
        corr, fig = Plotting.corrGrid(df, xaxis, yaxis, tipo, 0)

        xaxis, yaxis = Plotting.getCorrValues(corr)

        if len(xaxis)>0 and len(yaxis)>0:
            Plotting.checkFolders(nameBase, [subf])
            figName=nameBase+subf+tipo.replace(' ','').upper()+f"_{'species_' if singleAxis else ''}focusedCorrGrid_log_log.png"
            Plotting.corrGrid(df, list(set(xaxis)), list(set(yaxis)), tipo, 0.5)[1].savefig(figName, dpi=300, bbox_inches='tight')

            focusList = constants.initparams[tipo]
            Plotting.plottingGrid(df, yaxis, xaxis, tipo, nameBase+subf, focusList, constants.SCATTER)
            plt.close()

            if singleAxis: Plotting.contScatterPlot(df, xaxis, yaxis, tipo, nameBase+subf, [f'{prop}_log' for prop in constants.varPhys[tipo]])
            plt.close()