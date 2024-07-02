import uclchem, os, constants
import matplotlib.pyplot as plt
import pandas as pd

stage = constants.PHASE2

folder = '/data2/LEAPS-2024/Grid/2024-07-01_134429/{}/'
# stag1 = [f for f in os.listdir(folder.format(constants.PHASE1)) if 'startcollapse' not in f]
stag2 = [f for f in os.listdir(folder.format(constants.PHASE2)) if 'startcollapse' not in f]

def continuityPlot(runDict):
    df1= uclchem.analysis.read_output_file(runDict[0])
    df2= uclchem.analysis.read_output_file(runDict[1])
    cambio=df1['Time'].max()
    df2['Time']=df2['Time']+cambio
    df=pd.concat([df1,df2])
    species=['#CH3OH', 'CH3OH', '@CH3OH', '#SIO', 'SIO', 'SIO+', '@SIO']

    fig, axs = plt.subplots(2, 1, figsize=(14, 7))
    fig.subplots_adjust(wspace=0, hspace=0)
    fig.suptitle(runDict[2], size='large')

    axs[0]=uclchem.analysis.plot_species(axs[0],df,species)
    axs[0].axvline(cambio, c='black', ls='--', alpha=0.3)
    axs[0].set_xlim(left=cambio-1e6, right=cambio+1e6)
    # axs[0].set_xlim(left=df['Time'].min(), right=df['Time'].max())

    axs[1].plot(df['Time'], df['Density'], df['Time'], df['gasTemp'], df['Time'], df['av'])
    axs[1].axvline(cambio, c='black', ls='--', alpha=0.3)
    axs[1].set_xlim(left=cambio-1e6, right=cambio+1e6)
    # axs[1].set_xlim(left=df['Time'].min(), right=df['Time'].max())

    axs[0].legend(ncols=len(species), loc='lower left')
    axs[1].legend(['Density', 'gasTemp', 'av'])
       
    plt.savefig(folder.format('continuityPlots/zoom')+runDict[2]+'.png', bbox_inches='tight')

# stg1: dens - cosmic - ir rAD
# stg2: cosmic - ir rAD - dens - vel
for fileName in stag2:
    dic=dict()
    cosmic, irrAD, dens, vel = fileName.split('_')
    dic[0]=folder.format(constants.PHASE1)+'_'.join([str(dens),str(cosmic),str(irrAD)])+'.dat'
    dic[1]=folder.format(constants.PHASE2)+fileName
    dic[2]=fileName.strip('.dat')

    continuityPlot(dic)