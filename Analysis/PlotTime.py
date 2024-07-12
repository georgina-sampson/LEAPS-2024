import constants, Plotting, os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# folder = '{}'
folder = '/data2/gsampsonolalde/LEAPS-2024/Analysis/{}'
nameBase= folder.format('TimePlots/')

physical = {constants.SHOCK: ['Density', 'gasTemp', 'av', 'zeta', 'radfield', constants.SHOCKVEL],
            constants.HOTCORE: ['Density', 'gasTemp', 'av', 'zeta', 'radfield']}
species=['#CH3OH', 'CH3OH', '#SIO', 'SIO']


for tip in [constants.BAND, constants.SCATTER]:
    if not os.path.exists(nameBase+'/species/'+tip+'/'): os.makedirs(nameBase+'/species/'+tip+'/')
    if not os.path.exists(nameBase+'/physical/'+tip+'/'): os.makedirs(nameBase+'/physical/'+tip+'/')

for tipo in physical:
    print(tipo)
    focusList=constants.initparams[tipo]

    df= Plotting.buildDataframe(tipo, folder, physical, species)
    df['normalizedTime']= df['Time']/df.groupby('runName')['Time'].transform('max')
 
    yaxis= [f'{prop}_log' for prop in species]
    xaxis= [f'{prop}_log' for prop in physical[tipo]]

    for phys in xaxis:
        Plotting.timePlot(df, phys, tipo, nameBase+'physical/')
    
    for spec in yaxis:
        for focus in constants.initparams[tipo]:
            Plotting.timePlot(df, spec, tipo, nameBase+'species/', constants.SCATTER, focus)

    plt.close()