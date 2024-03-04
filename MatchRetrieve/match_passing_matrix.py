from typing import List, Dict

import networkx as nx
import numpy as np

import db_connect_utils
from data_type import PlayerCoordinate
from MatchRetrieve.match_info_retriever import MatchInfoRetriever

from database.database import Pass
from xThreat.xThreat import get_tile_id, xThreat


class MatchAdvancedPassingStats(MatchInfoRetriever):
    def __init__(self, match_id: str, side: str = "home"):
        super().__init__(match_id)

        self.side = side
        self.pass_count_matrix = self.get_pass_count_matrix()
        self.pass_xThreat_matrix = self.get_pass_xThreat_matrix()

    def get_pass_count_matrix(self):
        team_id: str = self.home_team_id if self.side == "home" else self.away_team_id
        start_time: int = self.home_longest_period_start_time if self.side == "home" \
            else self.away_longest_period_start_time
        end_time: int = self.home_longest_period_end_time if self.side == "home" else self.away_longest_period_end_time

        pass_events: List[Pass] = Pass.objects(match_id=self.match_id,
                                               team_id=team_id,
                                               outcome=1,
                                               time__gt=start_time,
                                               time__lt=end_time,
                                               destination_player__ne="0",
                                               origin_player__ne="0",
                                               )

        team_player_ids = self.home_team_players.nodes if self.side == "home" else self.away_team_players.nodes

        pass_count_dict: Dict[tuple[str, str]: int] = {(passer, receiver): 0 for passer in team_player_ids for receiver
                                                       in team_player_ids}

        pass_event: Pass
        for pass_event in pass_events:
            origin_player_id = pass_event.origin_player
            destination_player_id = pass_event.destination_player

            edge_name: tuple[str, str] = (origin_player_id, destination_player_id)
            pass_count_dict[edge_name] += 1

        team_graph = self.home_team_players if self.side == "home" else self.away_team_players
        for pass_receive, pass_count in pass_count_dict.items():
            team_graph.add_edge(pass_receive[0], pass_receive[1], pass_value=pass_count)

        passing_matrix: np.ndarray = np.array([pass_count for pass_count in pass_count_dict.values()]).reshape(11, 11)

        return passing_matrix

    def get_pass_xThreat_matrix(self, team_xThreat: str = "seasonal"):
        xThreat_array: np.ndarray
        if team_xThreat == "seasonal":
            seasonal_xThreat = np.genfromtxt("./xThreat/seasonal_xThreat.csv")
            xThreat_array = seasonal_xThreat
        else:
            team_xThreat_class = xThreat(team_name=team_xThreat)
            xThreat_array = team_xThreat_class.get_team_xThreat()

        team_id: str = self.home_team_id if self.side == "home" else self.away_team_id
        start_time: int = self.home_longest_period_start_time if self.side == "home" \
            else self.away_longest_period_start_time
        end_time: int = self.home_longest_period_end_time if self.side == "home" else self.away_longest_period_end_time
        pass_events: List[Pass] = Pass.objects(match_id=self.match_id,
                                               team_id=team_id,
                                               outcome=1,
                                               time__gt=start_time,
                                               time__lt=end_time,
                                               destination_player__ne="0",
                                               origin_player__ne="0",
                                               )
        team_player_ids = self.home_team_players.nodes if self.side == "home" else self.away_team_players.nodes

        pass_xThreat_dict: Dict[tuple[str, str]: float] = {(passer, receiver): 0.0 for passer in team_player_ids for
                                                           receiver in team_player_ids}
        pass_event: Pass
        for pass_event in pass_events:
            origin_player_id = pass_event.origin_player
            origin_player_x, origin_player_y = pass_event.origin_pos_x, pass_event.origin_pos_y
            origin_pos = PlayerCoordinate(origin_player_x, origin_player_y)
            origin_tile_id = get_tile_id(origin_pos)
            origin_xThreat = xThreat_array[origin_tile_id]

            destination_player_id = pass_event.destination_player
            destination_player_x, destination_player_y = pass_event.destination_pos_x, pass_event.destination_pos_y
            destination_pos = PlayerCoordinate(destination_player_x, destination_player_y)
            destination_tile_id = get_tile_id(destination_pos)
            destination_xThreat = xThreat_array[destination_tile_id]
            pass_xThreat_diff = destination_xThreat - origin_xThreat

            edge_name: tuple[str, str] = (origin_player_id, destination_player_id)
            pass_xThreat_dict[edge_name] += max(pass_xThreat_diff, 0)

        team_graph = self.home_team_players if self.side == "home" else self.away_team_players
        for pass_receive, xThreat_value in pass_xThreat_dict.items():
            team_graph.add_edge(pass_receive[0], pass_receive[1], xT_value=xThreat_value)

        passing_xThreat_matrix: np.ndarray = np.array(
            [xThreat_diff for xThreat_diff in pass_xThreat_dict.values()]).reshape(11, 11)

        return passing_xThreat_matrix

    def get_in_eigenvector_centrality(self, matrix_type="normal"):
        weight_type = "pass_value" if matrix_type == "normal" else "xT_value"
        team_graph = self.home_team_players if self.side == "home" else self.away_team_players

        eigenvector_centrality = np.array(list(nx.eigenvector_centrality_numpy(team_graph, weight=weight_type).values()))

        return eigenvector_centrality

    def get_out_eigenvector_centrality(self, matrix_type="normal"):
        adjacency_matrix = self.get_pass_count_matrix() if matrix_type == "normal" else self.get_pass_xThreat_matrix()
        adjacency_matrix = adjacency_matrix.transpose()
        initial_vector = np.ones(shape=11)
        for _ in range(100):
            initial_vector = np.dot(initial_vector, adjacency_matrix)
            initial_vector_norm = np.linalg.norm(initial_vector)
            initial_vector /= initial_vector_norm
            eigenvector_centrality = initial_vector

        return eigenvector_centrality
