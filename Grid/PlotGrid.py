import uclchem, os
import matplotlib.pyplot as plt

run='grid_2024-06-27_163339'


folder = f'/data2/LEAPS-2024/Grid/{run}/data/'
modelos = os.listdir(folder)

# temporary
species=["H","H2","$H","$H2","H2O","$H2O","CO","$CO","$CH3OH","CH3OH"]
fig, axs=plt.subplots(2,2,figsize=(20,20))
ejes=[axs[0][0],axs[0][1],axs[1][0],axs[1][1]]



for i in range(len(modelos)):
    result_df=uclchem.analysis.read_output_file(folder+modelos[i])
    ejes[i]=uclchem.analysis.plot_species(ejes[i],result_df,species)
    
    settings=ejes[i].set(yscale="log", xscale="log",
                         xlim=(1e2,1e6), ylim=(1e-10,1e-2),
                         xlabel="Time / years", ylabel="Fractional Abundance")

plt.show()