import constants, Plotting, os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# folder = '{}'
folder = constants.folder
nameBase= folder.format('LocalAbundancePlots/')

physical = constants.physical
species= constants.species

times={constants.HOTCORE: [constants.FINAL],
       constants.SHOCK: [constants.FINAL,constants.TMAX, constants.SHOCKAVG]}

for tipo in times:
    print(tipo)

    logPhysical= [f'{prop}_log' for prop in physical[tipo]]
    df= Plotting.buildDataframe(tipo, folder, physical, species)
    
    for time in times[tipo]:
        dfFinal= Plotting.localAbundanceDataframe(df, species, physical, tipo, momento=time)
        
        for phys in logPhysical+['species']:
            Plotting.localAbundancePlot(dfFinal, phys, tipo, nameBase, momento=time)
            
        plt.close()