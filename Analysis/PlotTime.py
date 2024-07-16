import constants, Plotting, os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# folder = '{}'
folder = constants.folder
nameBase= folder.format('TimePlots/')

physical = constants.physical
species= constants.species

for tipo in [constants.HOTCORE, constants.SHOCK]:
    print(tipo)
    focusList=constants.initparams[tipo]

    df= Plotting.buildDataframe(tipo, folder, physical, species)
 
    yaxis= [f'{prop}_log' for prop in species]
    xaxis= [f'{prop}_log' for prop in physical[tipo]]

    Plotting.timePlot(df, xaxis, tipo, nameBase+'physical/')
    
    for focus in constants.initparams[tipo]+constants.varPhys[tipo]:
        Plotting.timePlot(df, yaxis, tipo, nameBase+'species/', constants.SCATTER, focus)

    plt.close()