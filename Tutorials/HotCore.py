import uclchem
import matplotlib.pyplot as plt

# Initial Conditions (Phase 1)

# set a parameter dictionary for cloud collapse model
folder='/data2/LEAPS-2024/Tutorials/examples'
param_dict = {
    "endAtFinalDensity": False,#stop at finalTime
    "freefall": True,#increase density in freefall
    "initialDens": 1e2, #starting density
    "finalDens":1e6, #final density
    "initialTemp": 10.0,#temperature of gas
    "finalTime": 6.0e6, #final time
    "rout":0.1, #radius of cloud in pc
    "baseAv":1.0, #visual extinction at cloud edge.
    "abundSaveFile": folder+"/test-output/startcollapse.dat",#save final abundances to file
    "outputFile": folder+"/test-output/phase1-full.dat"

}
result = uclchem.model.cloud(param_dict=param_dict)
print('Phase 1', result)

# Running the Science Model (Phase 2)

#change other bits of input to set up phase 2
param_dict["initialDens"]=1e6
param_dict["finalTime"]=1e6
param_dict["freefall"]=False

#freeze out is completely overwhelmed by thermal desorption
#so turning it off has no effect on abundances but speeds up integrator.
param_dict["freezeFactor"]=0.0

# param_dict["abstol_factor"]=1e-18
# param_dict["reltol"]=1e-12

#pop is dangerous, it removes the original key so you can't rerun this cell.
param_dict["abundLoadFile"]=param_dict.pop("abundSaveFile") 
param_dict["outputFile"]=folder+"/test-output/phase2-full.dat"

result=uclchem.model.hot_core(temp_indx=3,max_temperature=300.0,param_dict=param_dict)
print('Phase 2', result)

phase2_df=uclchem.analysis.read_output_file(folder+"/test-output/phase2-full.dat")
uclchem.analysis.check_element_conservation(phase2_df)

species=["CO","H2O","CH3OH","#CO","#H2O","#CH3OH","@H2O","@CO","@CH3OH"]

fig,[ax,ax2]=plt.subplots(1,2,figsize=(16,9))
ax=uclchem.analysis.plot_species(ax,phase2_df,species)
settings=ax.set(yscale="log",xlim=(1e2,1e6),ylim=(1e-10,1e-2),
            xlabel="Time / years", 
            ylabel="Fractional Abundance",xscale="log")

ax2.plot(phase2_df["Time"],phase2_df["Density"],color="black")
ax2.set(xscale="log")
ax3=ax2.twinx()
ax3.plot(phase2_df["Time"],phase2_df["gasTemp"],color="red")
ax2.set(xlabel="Time / year",ylabel="Density")
ax3.set(ylabel="Temperature",facecolor="red",xlim=(1e2,1e6))
ax3.tick_params(axis='y', colors='red')
