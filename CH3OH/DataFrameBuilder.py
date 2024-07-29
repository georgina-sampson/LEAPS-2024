import os, constants, uclchem
import pandas as pd
import Plotting as pl

for tipoName, tipo in {constants.HOTCORE: constants.HOTCORE, constants.SHOCK: constants.SHOCK, constants.BOTH: [constants.HOTCORE, constants.SHOCK]}.items():
    df= pl.buildDataframe(tipo, constants.folder, constants.physical, constants.species, singleDf=False if tipoName==constants.BOTH else True)
    df.to_csv('/data2/gsampsonolalde/LEAPS-2024/CH3OH/windowsDf/'+tipoName+'.csv')