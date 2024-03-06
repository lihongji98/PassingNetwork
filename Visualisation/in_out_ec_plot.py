import pandas as pd
import matplotlib.pyplot as plt

in_data = pd.read_csv('in_eigenvector_centrality.csv')
out_data = pd.read_csv('out_eigenvector_centrality.csv')

pos = "goalkeeper"
# in_data = in_data[in_data["player_position"] == pos]
# out_data = out_data[out_data["player_position"] == pos]

player_name = in_data.player_name.values
in_pass_ec = in_data.pass_ec_mean.values
out_pass_ec = out_data.pass_ec_mean.values

in_xthreat_ec = in_data.xthreat_ec_mean.values
out_xthreat_ec = out_data.xthreat_ec_mean.values

position = in_data.player_position.values

colors = ["red", "orange", "blue", "green"]

for i, label in enumerate(position):
    if label == "striker":
        color = colors[0]
    elif label == "midfielder":
        color = colors[1]
    elif label == "defender":
        color = colors[2]
    else:
        color = colors[3]
    plt.scatter(in_pass_ec[i], out_pass_ec[i], color=color)

x = [0, 0.65]
plt.plot(x, x, linestyle='--', color='gray')

plt.xlabel('In pass Eigenvector Centrality')
plt.ylabel('Out pass Eigenvector Centrality')
plt.savefig(f"{pos}_in_out_pass_ec.png")
plt.show()
