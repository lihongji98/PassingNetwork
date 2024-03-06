import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

pos = "striker"
data = pd.read_csv('out_eigenvector_centrality.csv')
data = data[data["player_position"] == pos]
data = data[["player_name", "player_position", "pass_ec_mean", "xthreat_ec_mean"]]

pass_ec = data.pass_ec_mean.values
xthreat_ec = data.xthreat_ec_mean.values
player_names = data.player_name.values
player_positions = data.player_position.values


player_ec_dif = xthreat_ec - pass_ec

max_value = np.max(player_ec_dif)
min_value = np.min(player_ec_dif)
player_ec_dif = (player_ec_dif - min_value) / (max_value - min_value) - 0.1
print(set(player_positions))

plt.figure(dpi=500)

x = [0, 0.65]
print(x)
plt.plot(x, x, linestyle='--', color='gray')

cmap = plt.get_cmap('coolwarm')
colors = [cmap(dot) for dot in player_ec_dif]

plt.scatter(pass_ec, xthreat_ec, c=colors)

for i, label in enumerate(player_names):
    if 0.26 < xthreat_ec[i] or 0.25 < pass_ec[i]:
        plt.text(pass_ec[i], xthreat_ec[i], label, fontsize=6, ha='left', rotation=10)

plt.xlim(0, 0.4)
plt.ylim(0, 0.5)
plt.xlabel('Pass Eigenvector Centrality')
plt.ylabel('xThreat Eigenvector Centrality')

plt.savefig(f"{pos}_out_ec.png")
plt.show()
