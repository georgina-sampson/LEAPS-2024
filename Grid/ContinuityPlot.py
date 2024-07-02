import uclchem, os, constants
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

stage = constants.PHASE2

folder = '/data2/LEAPS-2024/Grid/2024-07-01_134429/{}/'
type= constants.SHOCK if '01_124848' in folder else constants.HOTCORE
# stag1 = [f for f in os.listdir(folder.format(constants.PHASE1)) if 'startcollapse' not in f]
stag2 = [f for f in os.listdir(folder.format(constants.PHASE2)) if 'startcollapse' not in f]

def continuityPlot(runDict):
    species=['#CH3OH', 'CH3OH', '@CH3OH', '#SIO', 'SIO', '@SIO']

    fig, axs = plt.subplots(2, 2, sharey='row', sharex='col', figsize=(14, 7))
    fig.subplots_adjust(wspace=0, hspace=0.1)
    fig.suptitle(runDict[3], size='large')

    for i in range(2):
        df= uclchem.analysis.read_output_file(runDict[i])
        ax1=axs[0][i]
        ax2=axs[1][i]

        ax1.set_prop_cycle('color',[plt.cm.copper(i) for i in np.linspace(0, 1, len(species))])
        ax1=uclchem.analysis.plot_species(ax1,df,species)
        ax1.set_ylim(bottom=1e-14, top=1)
        if i<1: ax1.set_xlim([0.0,df['Time'].max()])

        ax2.set_prop_cycle('color',[plt.cm.Dark2(i) for i in np.linspace(0, 1, 3)])
        ax2.plot(df['Time'], df['Density'], df['Time'], df['gasTemp'], df['Time'], df['av'])

    axs[0][0].legend(ncols=len(species), loc='upper left', mode='expand')
    axs[0][1].get_legend().remove()
    axs[1][0].legend(['Density', 'gasTemp', 'av'], ncols=3,loc='upper left')
    axs[1][1].set_xscale('log')
    axs[1][1].set_yscale('log')

    plt.savefig(folder.format('continuityPlots')+runDict[2]+'.png', bbox_inches='tight')

def plotDict(fileName, type):
    d=dict()
    cosmic, irrAD, dens, spec = fileName.split('_')
    d[0]=folder.format(constants.PHASE1)+'_'.join([str(dens),str(cosmic),str(irrAD)])+'.dat'
    d[1]=folder.format(constants.PHASE2)+fileName
    d[2]=fileName.strip('.dat')
    d[3]=f"Gas Density:{dens}, {'Shock Velocity' if type==constants.SHOCK else 'Hot Core Temperature'}:{spec.strip('.dat')}, Cosmic ray ionisation rate:{cosmic}, Interstellar radiation field:{irrAD}"
    return d

# stg1: dens - cosmic - ir rAD
# stg2: cosmic - ir rAD - dens - vel
for fileName in stag2:
    dic = plotDict(fileName, type)
    continuityPlot(dic)