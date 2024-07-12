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

tipo=constants.HOTCORE
print(tipo)

df= Plotting.buildDataframe(tipo, folder, physical, species)
df['normalizedTime']= df['Time']/df.groupby('runName')['Time'].transform('max')

dfFinal= Plotting.finalAbundanceDataframe(df, [f'{prop}_log' for prop in species])
 
logPhysical= [f'{prop}_log' for prop in physical[tipo]]

for phys in logPhysical+['species']:
    Plotting.finalAbundancePlot(dfFinal, phys, tipo, nameBase)

plt.close()