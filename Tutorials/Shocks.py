import uclchem
import matplotlib.pyplot as plt

# set a parameter dictionary for phase 1 collapse model
folder='/data2/gsampsonolalde/LEAPS-2024/Tutorials/examples'
param_dict = {
    "endAtFinalDensity": False,#stop at finalTime
    "freefall": True,#increase density in freefall
    "initialDens": 1e2, #starting density
    "finalDens":1e4, #final density
    "initialTemp": 10.0,#temperature of gas
    "finalTime": 6.0e6, #final time
    "rout":0.1, #radius of cloud in pc
    "baseAv":1.0, #visual extinction at cloud edge.
    "abundSaveFile": folder+"/test-output/shockstart.dat",
}
result = uclchem.model.cloud(param_dict=param_dict)
print('Phase 1', result)

# C-shock
#change other bits of input to set up phase 2
# param_dict["initialDens"]=1e4
# param_dict["finalTime"]=1e6
# if "abundSaveFile" in param_dict:
#     param_dict.pop("abundSaveFile")
# param_dict["abundLoadFile"]=folder+"/test-output/shockstart.dat"
# param_dict["outputFile"]=folder+"/test-output/cshock.dat"


# result=uclchem.model.cshock(shock_vel=40,param_dict=param_dict)
# result,dissipation_time=result

# phase2_df=uclchem.analysis.read_output_file(folder+"/test-output/cshock.dat")
# cons = uclchem.analysis.check_element_conservation(phase2_df)
# print('check_element_conservation', cons)

# species=["CO","H2O","CH3OH","NH3","$CO","$H2O","$CH3OH","$NH3"]

# fig,[ax,ax2]=plt.subplots(1,2,figsize=(16,9))
# ax=uclchem.analysis.plot_species(ax,phase2_df,species)
# settings=ax.set(yscale="log",xlim=(1,20*dissipation_time),ylim=(1e-10,1e-2),
#             xlabel="Time / years", 
#             ylabel="Fractional Abundance",xscale="log")

# ax2.plot(phase2_df["Time"],phase2_df["Density"],color="black")
# ax2.set(xscale="log")
# ax3=ax2.twinx()
# ax3.plot(phase2_df["Time"],phase2_df["gasTemp"],color="red")
# ax2.set(xlabel="Time / year",ylabel="Density")
# ax3.set(ylabel="Temperature",facecolor="red",xlim=(1,20*dissipation_time))
# ax3.tick_params(axis='y', colors='red')
# plt.show()

# J-shock
param_dict["initialDens"]=1e3
param_dict["freefall"]=False #lets remember to turn it off this time
param_dict["reltol"]=1e-12

shock_vel=10.0

if "abundSaveFile" in param_dict:
    param_dict.pop("abundSaveFile")
param_dict["abundLoadFile"]=folder+"/test-output/shockstart.dat"
param_dict["outputFile"]=folder+"/test-output/jshock.dat"


result=uclchem.model.jshock(shock_vel=shock_vel,param_dict=param_dict)
print(result)

phase2_df=uclchem.analysis.read_output_file(param_dict["outputFile"])
cons = uclchem.analysis.check_element_conservation(phase2_df)
print('check_element_conservation', cons)

species=["CO","H2O","CH3OH","NH3","$CO","$H2O","$CH3OH","$NH3"]

fig,[ax,ax2]=plt.subplots(1,2,figsize=(16,9))
ax=uclchem.analysis.plot_species(ax,phase2_df,species)
settings=ax.set(yscale="log",xlim=(1e-7,1e6),ylim=(1e-10,1e-2),
            xlabel="Time / years", 
            ylabel="Fractional Abundance",xscale="log")

ax2.plot(phase2_df["Time"],phase2_df["Density"],color="black")
ax2.set(xscale="log",yscale="log")
ax3=ax2.twinx()
ax3.plot(phase2_df["Time"],phase2_df["gasTemp"],color="red")
ax2.set(xlabel="Time / year",ylabel="Density")
ax3.set(ylabel="Temperature",facecolor="red",xlim=(1e-7,1e6))
ax3.tick_params(axis='y', colors='red')
plt.show()