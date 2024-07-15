import constants, Plotting, os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# folder = '{}'
folder = '/data2/gsampsonolalde/LEAPS-2024/Analysis/{}'
nameBase= folder.format('BothPlots/')

physical = {constants.SHOCK: ['Density', 'gasTemp', 'av', 'zeta', 'radfield', constants.SHOCKVEL],
            constants.HOTCORE: ['Density', 'gasTemp', 'av', 'zeta', 'radfield'],
            constants.BOTH: ['Density', 'gasTemp', 'av', 'zeta', 'radfield']}
species=['#CH3OH', 'CH3OH', '#SIO', 'SIO']

for tip in ['',constants.TIME+'/', constants.ABUNDANCE+'/']:
    if not os.path.exists(nameBase+tip): os.makedirs(nameBase+tip)


df=Plotting.buildDataframe([constants.HOTCORE, constants.SHOCK], folder, physical, species, singleDf=False)
df['normalizedTime']= df['Time']/df.groupby('runName')['Time'].transform('max')
jointDf=Plotting.localAbundanceDataframe(df, species, physical, constants.BOTH, constants.ALL, singleDf=False)
jointDf['normalizedTime_log']= np.log10(jointDf['normalizedTime'])

Plotting.typeAbundanceGrid(jointDf, physical[constants.BOTH], nameBase)
plt.close()
Plotting.typePhysicalGrid(df, physical[constants.BOTH], species, nameBase)
plt.close()