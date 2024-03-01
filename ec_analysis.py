import pandas as pd
from db_connect_utils import db_connect, db_disconnect
from database.database import Player, Team


def match_team():
    ec_data = pd.read_csv("eigenvector_centrality.csv").dropna()
    print(ec_data)

    team_dict = {}
    for team in Team.objects():
        team_name = team.team_name
        team_id = team.team_id
        team_dict[team_id] = team_name

    player_team_column = []
    player_minute_column = []
    player_position_column = []
    player_name_column = []

    sub_counter = 0
    for index, row in ec_data.iterrows():
        player_id = str(int(row["player_id"]))
        current_player: Player = Player.objects(player_id=player_id).first()
        player_team_column.append(team_dict[current_player.team_id[0]])
        player_minute = current_player.minutes
        player_minute_column.append(player_minute)
        player_name_column.append(current_player.known_name)
        player_position_list = sorted(current_player.position.items(), key=lambda x: x[1], reverse=True)

        if player_position_list[0][0] == "substitute":
            if player_position_list[1][1] > 0:
                player_position = player_position_list[1][0]
            else:
                player_position = "substitute"
                sub_counter += 1
        else:
            player_position = player_position_list[0][0]
        player_position_column.append(player_position)

    ec_data["player_team"] = player_team_column
    ec_data["player_minute"] = player_minute_column
    ec_data["player_position"] = player_position_column
    ec_data["player_name"] = player_name_column
    # team_ec_data = ec_data.groupby("player_team")

    ec_data = ec_data[ec_data["player_position"] != "substitute"]

    ec_data.to_csv('eigenvector_centrality.csv', index=False)


def groupby_team_data():
    # key_list = ["player_id",
    #             "pass_ec_mean", "pass_ec_std",
    #             "xthreat_ec_mean", "xthreat_ec_std",
    #             "difference_ec_mean", "difference_ec_std"]
    minute_threshold = 200
    team_data = pd.read_csv("eigenvector_centrality.csv")
    team_data = team_data[team_data['player_minute'] >= minute_threshold]
    team_groupby_data = team_data.groupby("player_position")
    print(team_data)
    metric_name = "xthreat_ec_mean"
    metric_type = "xthreat_ec"
    for index, team_data in team_groupby_data:
        team_data = team_data.sort_values(by=[metric_name], ascending=False)
        team_data = team_data[["player_team", "player_name", "player_minute", metric_name]]
        team_data.to_csv(f"./player_ec_rank/{index}_{metric_type}.csv")
        print(index, team_data)
        print("\n")


# db_connect()

# match_team()
groupby_team_data()

db_disconnect()
