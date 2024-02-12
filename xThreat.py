from typing import Dict
import networkx as nx
import numpy as np
import pandas as pd
from tqdm import tqdm

from PitchData import pitch_graph
from config import PitchMeta
from data_type import (
    PlayerCoordinate,
    TileStatsFeatures,
    TileStateDistribution,
    ConversionRate,
    TileID
)


def get_tile_id(player_pos: PlayerCoordinate):
    player_x, player_y = player_pos.x, player_pos.y
    distance_buffer = []
    for tile_id in pitch_graph.nodes:
        center_x = pitch_graph.nodes[tile_id]["pos_info"].center_x
        center_y = pitch_graph.nodes[tile_id]["pos_info"].center_y

        current_distance = np.sqrt((player_x - center_x) ** 2 + (player_y - center_y) ** 2)
        distance_buffer.append([tile_id, current_distance])
    current_tile: int = sorted(distance_buffer, key=lambda x: x[1])[0][0]

    return current_tile


class xThreat:
    def __init__(self, _pitch_graph: nx.Graph):
        self.pitch_graph: nx.Graph = _pitch_graph
        self.xThreat_surface: np.ndarray = np.zeros(len(self.pitch_graph.nodes))

    def fit_retrieve_data(self, _data: pd.DataFrame):
        df_shot = _data[_data.codigo.isin([13, 14, 15, 16])]
        df_goal = df_shot[df_shot.codigo == 16]
        df_pass = _data[_data.codigo.isin([1])]

        for index, row in df_shot.iterrows():
            shot_pos = PlayerCoordinate(row.x, row.y)
            tile_id = get_tile_id(shot_pos)
            stats_info: TileStatsFeatures = self.pitch_graph.nodes[tile_id]["stats_info"]
            stats_info.shot_count += 1

        for index, row in df_goal.iterrows():
            goal_pos = PlayerCoordinate(row.x, row.y)
            tile_id = get_tile_id(goal_pos)
            stats_info: TileStatsFeatures = self.pitch_graph.nodes[tile_id]["stats_info"]
            stats_info.goal_count += 1

        for index, row in df_pass.iterrows():
            origin_pos = PlayerCoordinate(row.x, row.y)
            destination_pos = PlayerCoordinate(row.end_x, row.end_y)
            origin_tile_id = get_tile_id(origin_pos)
            destination_tile_id = get_tile_id(destination_pos)
            stats_info: TileStatsFeatures = self.pitch_graph.nodes[origin_tile_id]["stats_info"]
            stats_info.pass_count_surface[destination_tile_id] += 1

    def _get_state_prob_distribution(self):
        state_prob_distribution_dict: Dict[TileID, TileStateDistribution] = {}
        for tile_id in self.pitch_graph.nodes:
            stats_info: TileStatsFeatures = self.pitch_graph.nodes[tile_id]["stats_info"]
            shot_count = stats_info.shot_count
            pass_count = np.sum(stats_info.pass_count_surface)
            shot_pass_sum = shot_count + pass_count

            shot_prob = shot_count / shot_pass_sum if shot_pass_sum > 0 else 0
            pass_prob = pass_count / shot_pass_sum if shot_pass_sum > 0 else 0

            tile_state_prob_distribution = TileStateDistribution(shot_prob, pass_prob)
            state_prob_distribution_dict[tile_id] = tile_state_prob_distribution

        return state_prob_distribution_dict

    def _get_scoring_percentage(self):
        tile_conversion_dict: Dict[TileID, ConversionRate] = {}
        for tile_id in self.pitch_graph.nodes:
            stats_info: TileStatsFeatures = self.pitch_graph.nodes[tile_id]["stats_info"]
            shot_count = stats_info.shot_count
            goal_count = stats_info.goal_count

            conversion_rate = goal_count / shot_count if shot_count > 0 else 0
            tile_conversion_dict[tile_id] = conversion_rate
        return tile_conversion_dict

    def _get_pass_distribution(self):
        tile_pass_distribution_dict: Dict[TileID, np.ndarray] = {}
        for tile_id in self.pitch_graph.nodes:
            stats_info: TileStatsFeatures = self.pitch_graph.nodes[tile_id]["stats_info"]
            pass_count_surface = stats_info.pass_count_surface
            total_pass_count = np.sum(pass_count_surface)

            pass_distribution = pass_count_surface / total_pass_count if total_pass_count != 0 else np.zeros_like(pass_count_surface)

            tile_pass_distribution_dict[tile_id] = pass_distribution
        return tile_pass_distribution_dict

    def compute_xThreat(self, _xThreat):
        state_probs_shot_pass = self._get_state_prob_distribution()
        state_probs_shot_goal = self._get_scoring_percentage()
        transmission_matrix = self._get_pass_distribution()

        assert _xThreat.shape[0] == len(self.pitch_graph.nodes), "xThreat shape does not match pitch graph key number"

        current_xThreat = _xThreat.copy()
        for tile_id in self.pitch_graph.nodes:
            assert transmission_matrix[tile_id].shape == _xThreat.shape, "Transmission matrix does not match xThreat shape"

            pass_payoff = np.sum(transmission_matrix[tile_id] * current_xThreat)
            pass_value = state_probs_shot_pass[tile_id].pass_prob * pass_payoff
            shot_value = state_probs_shot_pass[tile_id].shot_prob * state_probs_shot_goal[tile_id]
            _xThreat[tile_id] = pass_value + shot_value

        return _xThreat

    def train(self, epochs):
        for epoch in tqdm(range(epochs)):
            xThreat_buffer = self.xThreat_surface.copy()
            self.xThreat_surface = self.compute_xThreat(self.xThreat_surface)
            xThreat_error = np.sum(xThreat_buffer - self.xThreat_surface)
            print(epoch, xThreat_error)
            if abs(xThreat_error) < 1e-6:
                break

        self.xThreat_surface = np.round(self.xThreat_surface, 1)


data = pd.read_csv("demo_data/2372222_all_events.txt", sep="\t")

xx = xThreat(pitch_graph)
xx.fit_retrieve_data(data)
xx.train(1000)
print(xx.xThreat_surface.reshape(PitchMeta.y, PitchMeta.x))
