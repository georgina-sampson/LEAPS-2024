import constants, Plotting, os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# folder = '{}'
folder = constants.folder
nameBase= folder.format('AbundancePlots/')

physical = constants.physical
species= constants.species

for tipo in [constants.HOTCORE, constants.SHOCK]:
    print(tipo)

    df= Plotting.buildDataframe(tipo, folder, physical, species)
    dfFinal= Plotting.localAbundanceDataframe(df, species, physical, tipo)
    
    logPhysical= [f'{prop}_log' for prop in physical[tipo]]

    for phys in logPhysical+['species']:
        Plotting.localAbundancePlot(dfFinal, phys, tipo, nameBase)

        if tipo == constants.SHOCK:
            dfFinal= Plotting.localAbundanceDataframe(df, species, physical, tipo, constants.TMAX)
            Plotting.localAbundancePlot(dfFinal, phys, tipo, nameBase, constants.TMAX)
            dfFinal= Plotting.localAbundanceDataframe(df, species, physical, tipo, constants.SHOCKAVG)
            Plotting.localAbundancePlot(dfFinal, phys, tipo, nameBase, constants.SHOCKAVG)

    plt.close()