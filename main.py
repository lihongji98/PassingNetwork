from typing import Dict, List

import numpy as np
import pandas as pd
from tqdm import tqdm

from db_connect_utils import db_connect, db_disconnect
from MatchRetrieve.match_passing_matrix import MatchAdvancedPassingStats
from database.database import Match, Player
from data_type import MatchPlayerEigenvectorCentralityInfo


def get_player_pass_xthreat_difference():
    player_stats_eigenvector_centrality_dict: Dict[str: List[MatchPlayerEigenvectorCentralityInfo]] = {}
    for player in Player.objects():
        player_id = player.player_id
        player_stats_eigenvector_centrality_dict[player_id] = []

    match_id_set = set()
    match_event: Match
    for match_event in Match.objects():
        match_id_set.add(match_event.match_id)
    match_id_set = sorted(match_id_set)

    for match_id in tqdm(match_id_set):
        for side in ["home", "away"]:
            match_info_container = MatchAdvancedPassingStats(match_id=match_id, side=side)
            player_list = match_info_container.home_team_players.nodes \
                if side == "home" else match_info_container.away_team_players.nodes

            pass_EC = match_info_container.get_eigenvector_centrality(matrix_type="normal")
            xThreat_EC = match_info_container.get_eigenvector_centrality(matrix_type="xThreat")

            for player_id, pass_EC, xThreat_EC in zip(player_list, pass_EC, xThreat_EC):
                ec_info = MatchPlayerEigenvectorCentralityInfo(pass_EC, xThreat_EC)
                player_stats_eigenvector_centrality_dict[player_id].append(ec_info)

    key_list = ["player_id",
                "pass_ec_mean", "pass_ec_std",
                "xthreat_ec_mean", "xthreat_ec_std",
                "difference_ec_mean", "difference_ec_std"]
    output_dict = {key_name: [] for key_name in key_list}
    for player_id in player_stats_eigenvector_centrality_dict.keys():
        stats_items: List[MatchPlayerEigenvectorCentralityInfo] = player_stats_eigenvector_centrality_dict[player_id]

        pass_ec = np.array([stats_item.pass_eigenvector_centrality for stats_item in stats_items])
        xthreat_ec = np.array([stats_item.xthreat_eigenvector_centrality for stats_item in stats_items])
        difference_ec = np.array([stats_item.xthreat_eigenvector_centrality - stats_item.pass_eigenvector_centrality \
                                  for stats_item in stats_items])

        pass_ec_mean, pass_ec_std = np.mean(pass_ec), np.std(pass_ec)
        if pass_ec_mean < 0:
            print(pass_ec)
        xthreat_ec_mean, xthreat_ec_std = np.mean(xthreat_ec), np.std(xthreat_ec)
        difference_ec_mean, difference_ec_std = np.mean(difference_ec), np.std(difference_ec)

        output_dict["player_id"].append(player_id)
        output_dict["pass_ec_mean"].append(pass_ec_mean)
        output_dict["pass_ec_std"].append(pass_ec_std)
        output_dict["xthreat_ec_mean"].append(xthreat_ec_mean)
        output_dict["xthreat_ec_std"].append(xthreat_ec_std)
        output_dict["difference_ec_mean"].append(difference_ec_mean)
        output_dict["difference_ec_std"].append(difference_ec_std)

    eigenvector_centrality_stats = pd.DataFrame(output_dict)
    eigenvector_centrality_stats.to_csv('eigenvector_centrality.csv', index=False)


def main():
    db_connect()
    get_player_pass_xthreat_difference()
    # aa = MatchAdvancedPassingStats(match_id="2372229", side="away")  # '73314'
    # print(aa.away_team_players.nodes)
    # pass_ec = aa.get_eigenvector_centrality(matrix_type="normal")
    # print(pass_ec)
    # print(xthreat_ec)
    # print(pass_ec - xthreat_ec)
    db_disconnect()


if __name__ == '__main__':
    main()
