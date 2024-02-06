from typing import List, Dict
import networkx as nx
import numpy as np

from PitchData import pitch_graph
from data_type import (
    PlayerCoordinate,
    TileStatsFeatures,
    TileStateDistribution, ConversionRate, TileID
)


def get_tile_id(player_pos: PlayerCoordinate):
    player_x, player_y = player_pos.x, player_pos.y
    distance_buffer = []
    for tile_id in pitch_graph.nodes:
        center_x = pitch_graph.nodes[tile_id]["pos_info"].center_x
        center_y = pitch_graph.nodes[tile_id]["pos_info"].center_y

        current_distance = np.sqrt((player_x - center_x) ** 2 + (player_y - center_y) ** 2)
        distance_buffer.append([tile_id, current_distance])
    current_tile = sorted(distance_buffer, key=lambda x: x[1])[0][0]

    return current_tile


class xThreat:
    def __init__(self, _pitch_graph: nx.Graph):
        self.pitch_graph: nx.Graph = _pitch_graph
        self.xThreat_surface: np.ndarray = np.zeros(len(self.pitch_graph.nodes))

        self.state_prob_distribution_dict: Dict[TileID, TileStateDistribution] = {}
        self.tile_conversion_dict: Dict[TileID, ConversionRate] = {}
        self.tile_pass_distribution_dict: Dict[TileID, np.ndarray] = {}

    def _get_state_prob_distribution(self):
        for tile_id in self.pitch_graph.nodes:
            stats_info: TileStatsFeatures = self.pitch_graph.nodes[tile_id]["stats_info"]
            shot_count = stats_info.shot_count
            pass_count = np.sum(stats_info.pass_count_surface)
            shot_pass_sum = shot_count + pass_count

            shot_prob = shot_count / shot_pass_sum if shot_pass_sum > 0 else 0
            pass_prob = pass_count / shot_pass_sum if shot_pass_sum > 0 else 0

            tile_state_prob_distribution = TileStateDistribution(shot_prob, pass_prob)
            self.state_prob_distribution_dict[tile_id] = tile_state_prob_distribution

    def _get_scoring_percentage(self):
        for tile_id in self.pitch_graph.nodes:
            stats_info: TileStatsFeatures = self.pitch_graph.nodes[tile_id]["stats_info"]
            shot_count = stats_info.shot_count
            goal_count = stats_info.goal_count
            shot_goal_sum = shot_count + goal_count

            conversion_rate = goal_count / shot_goal_sum if shot_goal_sum > 0 else 0
            self.tile_conversion_dict[tile_id] = conversion_rate

    def _get_pass_distribution(self):
        for tile_id in self.pitch_graph.nodes:
            stats_info: TileStatsFeatures = self.pitch_graph.nodes[tile_id]["stats_info"]
            pass_count_surface = stats_info.pass_count_surface
            total_pass_count = np.sum(pass_count_surface)

            pass_distribution = pass_count_surface / total_pass_count if total_pass_count != 0 else \
                np.zeros_like(pass_count_surface)

            self.tile_pass_distribution_dict[tile_id] = pass_distribution

    def compute_xThreat(self, _xThreat):
        self._get_state_prob_distribution()
        self._get_scoring_percentage()
        self._get_pass_distribution()
        state_probs_shot_pass = self.state_prob_distribution_dict
        transmission_matrix = self.tile_pass_distribution_dict
        state_probs_shot_goal = self.tile_conversion_dict

        assert _xThreat.shape[0] == len(self.pitch_graph.nodes), "xThreat shape does not match pitch graph key number"

        current_xThreat = _xThreat.copy()
        for tile_id in self.pitch_graph.nodes:

            assert transmission_matrix[tile_id].shape == _xThreat.shape, \
                "Transmission matrix does not match xThreat shape"

            pass_payoff = np.sum(transmission_matrix[tile_id] * current_xThreat)
            pass_value = state_probs_shot_pass[tile_id].pass_prob * pass_payoff
            shot_value = state_probs_shot_pass[tile_id].shot_prob * state_probs_shot_goal[tile_id]
            _xThreat[tile_id] = pass_value + shot_value

        return _xThreat

    def train(self, epochs):
        for _ in range(epochs):
            self.xThreat_surface = self.compute_xThreat(self.xThreat_surface)


xx = xThreat(pitch_graph)
xx.train(1)
print(xx.xThreat_surface)
