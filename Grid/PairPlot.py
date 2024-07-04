import uclchem, os, constants
import pandas as pd
import seaborn as sns

folder = '/data2/gsampsonolalde/LEAPS-2024/Grid/2024-07-01_{}/{}/'
li=[f for f in os.listdir(folder.format('124848', constants.PHASE2)) if 'startcollapse' not in f]
df_sh = pd.concat([uclchem.analysis.read_output_file(folder.format('124848', constants.PHASE2)+gg) for gg in li])
# li=[f for f in os.listdir(folder.format('134429', constants.PHASE2)) if 'startcollapse' not in f]
# df_hc = pd.concat([uclchem.analysis.read_output_file(folder.format('134429', constants.PHASE2)+gg) for gg in li])
hydrogen=['H', '#H', 'H+', '@H', 'H2', '#H2', 'H2+', '@H2']
species=['#CH3OH', 'CH3OH', '@CH3OH', '#SIO', 'SIO', '@SIO']

df_sh= df_sh.loc[:,['Time', 'Density', 'gasTemp', 'av', 'zeta']+species]
# df_hc= df_hc.loc[:,['Time', 'Density', 'gasTemp', 'av', 'zeta']+species]

# sns.pairplot(df_hc).savefig('/data2/gsampsonolalde/LEAPS-2024/Grid/2024-07-01_134429/PairPlot_HC.png')
sns.pairplot(df_sh).savefig('/data2/gsampsonolalde/LEAPS-2024/Grid/2024-07-01_124848/PairPlot_SH.png')
