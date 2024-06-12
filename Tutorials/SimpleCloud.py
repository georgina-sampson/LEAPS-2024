import uclchem

# set a parameter dictionary for phase 1 collapse model
folder='/data2/LEAPS-2024/Tutorials/examples'

out_species = ["SO","CO"]
param_dict = {
    "endAtFinalDensity": False,#stop at finalTime
    "freefall": False,#don't increase density in freefall
    "initialDens": 1e4, #starting density
    "initialTemp": 10.0,#temperature of gas
    "finalTime": 1.0e6, #final time
    "rout":0.1, #radius of cloud in pc
    "baseAv":1.0, #visual extinction at cloud edge.
    "outputFile": folder+"/test-output/static-full.dat",#full UCLCHEM output
    "abundSaveFile": folder+"/test-output/startstatic.dat",#save final abundances to file
}
result = uclchem.model.cloud(param_dict=param_dict,out_species=out_species)
print(result)

result_df=uclchem.analysis.read_output_file(folder+"/test-output/static-full.dat")
result_df.head()

conservation=uclchem.analysis.check_element_conservation(result_df,element_list=["H","N","C","O","S"])
print("Percentage change in total abundances:")
print(conservation)

species=["H","H2","$H","$H2","H2O","$H2O","CO","$CO","$CH3OH","CH3OH"]
fig,ax=uclchem.analysis.create_abundance_plot(result_df,species,figsize=(10,7))
ax=ax.set(xscale="log",ylim=(1e-15,1),xlim=(1e3,1e6))
