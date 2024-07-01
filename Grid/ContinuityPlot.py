import uclchem, os, constants
import matplotlib.pyplot as plt

stage = constants.PHASE2

folder = '/data2/LEAPS-2024/Grid/2024-07-01_134429/{}/'
# stag1 = [f for f in os.listdir(folder.format(constants.PHASE1)) if 'startcollapse' not in f]
stag2 = [f for f in os.listdir(folder.format(constants.PHASE2)) if 'startcollapse' not in f]

# stg1: dens - cosmic - ir rAD
# stg2: cosmic - ir rAD - dens - vel
pairs = []
for f in stag2:
    d=dict()
    cosmic, irrAD, dens, vel = f.split('_')
    d[1]=folder.format(constants.PHASE1)+'_'.join([str(dens),str(cosmic),str(irrAD)])+'.dat'
    d[2]=folder.format(constants.PHASE2)+f
    d[3]=f.strip('.dat')
    pairs.append(d)

# temporary
hydrogen=['H', '#H', 'H+', '@H', 'H2', '#H2', 'H2+', '@H2']
species=["#H2O","#CO","#CH3OH","CO","CH3OH","H2O"]
fig, axs=plt.subplots(2,2,figsize=(10,10),layout='constrained', sharey='row')

for pera in pairs:
    df1=uclchem.analysis.read_output_file(pera[1])
    df2=uclchem.analysis.read_output_file(pera[2])

    axs[0][0]=uclchem.analysis.plot_species(axs[0][0],df1,species)
    axs[0][1]=uclchem.analysis.plot_species(axs[0][1],df2,species)
        
    axs[0][0].set(yscale="log", xscale="log",
                        # ylim=(1e-14,1e0),
                        xlim=(None,4.500E+06),
                        # xlabel="Time / years", ylabel="Fractional Abundance"
                        )
    axs[0][1].set(yscale="log", xscale="log",
                        # ylim=(1e-14,1e0),
                        # xlabel="Time / years", ylabel="Fractional Abundance"
                        )
    
    axs[1][0].plot(df1.Time, df1.Density, df1.Time, df1.gasTemp, df1.Time, df1.av)
    axs[1][1].plot(df2.Time, df2.Density, df2.Time, df2.gasTemp, df2.Time, df2.av)
        
    axs[1][0].set(xscale="log",xlim=(None,4.500E+06))
    axs[1][1].set(xscale="log")
    axs[1][0].legend(['Density', 'gasTemp', 'Av'])
    axs[1][1].legend(['Density', 'gasTemp', 'Av'])

    # plt.show()
    plt.savefig(folder.format('consistencyPlots')+pera[3]+'.png', bbox_inches='tight')