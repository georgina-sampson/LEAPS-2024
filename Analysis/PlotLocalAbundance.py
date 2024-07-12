import constants, Plotting, os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# folder = '{}'
folder = '/data2/gsampsonolalde/LEAPS-2024/Analysis/{}'
nameBase= folder.format('AbundancePlots/')

physical = {constants.SHOCK: ['Density', 'gasTemp', 'av', 'zeta', 'radfield', constants.SHOCKVEL],
            constants.HOTCORE: ['Density', 'gasTemp', 'av', 'zeta', 'radfield']}
species=['#CH3OH', 'CH3OH', '#SIO', 'SIO']


for tip in ['']:
    if not os.path.exists(nameBase+tip+'/'): os.makedirs(nameBase+tip+'/')

for tipo in physical:
    print(tipo)

    df= Plotting.buildDataframe(tipo, folder, physical, species)
    df['normalizedTime']= df['Time']/df.groupby('runName')['Time'].transform('max')

    dfFinal= Plotting.localAbundanceDataframe(df, [f'{prop}_log' for prop in species], physical, tipo)
    
    logPhysical= [f'{prop}_log' for prop in physical[tipo]]

    for phys in logPhysical+['species']:
        Plotting.localAbundancePlot(dfFinal, phys, tipo, nameBase)

    if tipo == constants.SHOCK:
        dfFinal= Plotting.localAbundanceDataframe(df, [f'{prop}_log' for prop in species], physical, tipo, constants.TMAX)
        Plotting.localAbundancePlot(dfFinal, phys, tipo, nameBase, constants.TMAX)

    plt.close()