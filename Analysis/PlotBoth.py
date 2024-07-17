import constants, Plotting
import matplotlib.pyplot as plt

# folder = '{}'
folder = constants.folder
nameBase= folder.format('BothPlots/')

physical = constants.physical
species= constants.species


df=Plotting.buildDataframe([constants.HOTCORE, constants.SHOCK], folder, physical, species, singleDf=False)
jointDf=Plotting.localAbundanceDataframe(df, species, physical, constants.BOTH, constants.ALL, singleDf=False)

Plotting.typePhysicalGrid(df, physical[constants.BOTH], species, nameBase)

Plotting.typeAbundanceGrid(jointDf, physical[constants.BOTH], nameBase)
Plotting.abundanceScater(jointDf, 'zeta_log', 'species', nameBase)
plt.close()