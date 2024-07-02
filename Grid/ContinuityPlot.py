import uclchem, os, constants
import matplotlib.pyplot as plt

stage = constants.PHASE2

folder = '/data2/LEAPS-2024/Grid/2024-07-01_124848/{}/'
# stag1 = [f for f in os.listdir(folder.format(constants.PHASE1)) if 'startcollapse' not in f]
stag2 = [f for f in os.listdir(folder.format(constants.PHASE2)) if 'startcollapse' not in f]

def continuityPlot(runDict):
    species=['#CH3OH', 'CH3OH', '@CH3OH', '#SIO', 'SIO', 'SIO+', '@SIO']

    fig, axs = plt.subplots(2, 2, sharey='row', figsize=(14, 7))
    fig.subplots_adjust(wspace=0, hspace=0)
    fig.suptitle(runDict[2], size='large')

    for i in range(2):
        df= uclchem.analysis.read_output_file(runDict[i])
        ax1=axs[0][i]
        ax2=axs[1][i]

        ax1=uclchem.analysis.plot_species(ax1,df,species)
        ax1.set_xlim(left=df['Time'].min(), right=df['Time'].max())

        ax2.plot(df['Time'], df['Density'], df['Time'], df['gasTemp'], df['Time'], df['av'])
        ax2.set_xlim(left=df['Time'].min(), right=df['Time'].max())
    
    axs[0][0].get_legend().remove()
    axs[1][1].legend(['Density', 'gasTemp', 'av'])
       
    plt.savefig(folder.format('continuityPlots')+runDict[2]+'.png', bbox_inches='tight')

# stg1: dens - cosmic - ir rAD
# stg2: cosmic - ir rAD - dens - vel
for fileName in stag2:
    d=dict()
    cosmic, irrAD, dens, vel = fileName.split('_')
    d[0]=folder.format(constants.PHASE1)+'_'.join([str(dens),str(cosmic),str(irrAD)])+'.dat'
    d[1]=folder.format(constants.PHASE2)+fileName
    d[2]=fileName.strip('.dat')

    continuityPlot(d)