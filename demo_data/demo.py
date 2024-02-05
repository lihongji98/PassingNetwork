import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from data_type import (
    TileID, ConversionRate,
    PlayerCoordinate,
    TileStateCount,
    TileStateDistribution,
    TileShotGoalCount
)
from config import PitchMeta


def get_the_closest_tile(player_coordinate: PlayerCoordinate):
    # the pitch size is 100 * 100, and converted to 16 * 12
    tile_x = player_coordinate.x // (100 / PitchMeta.x) if player_coordinate.x < 100 else PitchMeta.x - 1
    tile_y = player_coordinate.y // (100 / PitchMeta.y) if player_coordinate.y < 100 else PitchMeta.y - 1

    tile_id = PitchMeta.x * tile_y + tile_x if tile_y != 0 else tile_x

    return tile_id


def initialise_pitch_graph(_df_all_events):
    df_shot = _df_all_events[_df_all_events.codigo.isin([13, 14, 15, 16])]
    df_goal = df_shot[df_shot.codigo == 16]
    df_pass = _df_all_events[_df_all_events["tipo"] == "pase"]

    pitch_graph = {i: [0, 0, np.zeros(shape=(PitchMeta.x * PitchMeta.y))] for i in range(PitchMeta.x * PitchMeta.y)}
    surface = pitch_graph[0][2]

    for index, row in df_shot.iterrows():
        shot_pos = PlayerCoordinate(row.x, row.y)
        tile_id = get_the_closest_tile(shot_pos)
        pitch_graph[tile_id][0] += 1

    print(pitch_graph)


def _get_tile_state_probs(shot_pass_count_dict: Dict[TileID, TileStateCount]) -> Dict[TileID, TileStateDistribution]:
    tile_state_distribution_dict: Dict[TileID, TileStateDistribution] = {}
    for index, tile_id in enumerate(shot_pass_count_dict.keys()):
        tile_state_info: TileStateCount = shot_pass_count_dict[tile_id]
        shot_count = tile_state_info.shot_count
        pass_count = tile_state_info.pass_count

        shot_ratio = shot_count / (pass_count + shot_count)
        pass_ratio = pass_count / (pass_count + shot_count)

        tile_state_distribution = TileStateDistribution(shot_ratio, pass_ratio)

        tile_state_distribution_dict[tile_id] = tile_state_distribution

    return tile_state_distribution_dict


def _get_pass_distribution(pass_count_dict: Dict[TileID, np.ndarray]) -> Dict[TileID, np.ndarray]:
    tile_pass_distribution_dict: Dict[TileID, np.ndarray] = {}
    for index, tile_id in enumerate(pass_count_dict.keys()):
        pass_count_distribution = pass_count_dict[tile_id]
        pass_count_total = np.sum(pass_count_distribution)
        pass_distribution = pass_count_distribution / pass_count_total

        tile_pass_distribution_dict[tile_id] = pass_distribution

    return tile_pass_distribution_dict


def _get_scoring_percentage(shot_goal_count_dict: Dict[TileID, TileShotGoalCount]) -> Dict[TileID, ConversionRate]:
    tile_conversion_rate_dict: Dict[TileID, ConversionRate] = {}
    for index, tile_id in enumerate(shot_goal_count_dict.keys()):
        goal_count = shot_goal_count_dict[tile_id].goal_count
        shot_count = shot_goal_count_dict[tile_id].shot_count
        scoring_percentage = goal_count / shot_count

        tile_conversion_rate_dict[tile_id] = scoring_percentage

    return tile_conversion_rate_dict


def _get_xThreat_materials(
        pitch_graph: Dict[TileID, Tuple[int, int, np.ndarray]]):  # List[shot, goal, pass_count_surface]
    shot_pass_count_dict = {}
    for tile_id in pitch_graph.keys():
        shot_count = pitch_graph[tile_id][0]
        pass_count = np.sum(pitch_graph[tile_id][2])
        shot_pass_count_dict[tile_id] = TileStateCount(shot_count, pass_count)
    tile_state_distribution_dict = _get_tile_state_probs(shot_pass_count_dict)

    pass_count_dict = {}
    for tile_id in pitch_graph.keys():
        pass_surface = pitch_graph[tile_id][2]
        pass_count_dict[tile_id] = pass_surface
    tile_pass_distribution_dict = _get_pass_distribution(pass_count_dict)

    shot_goal_count_dict = {}
    for tile_id in pitch_graph.keys():
        shot_count = pitch_graph[tile_id][0]
        goal_count = pitch_graph[tile_id][1]
        shot_goal_count_dict[tile_id] = TileShotGoalCount(shot_count, goal_count)
    tile_conversion_rate_dict = _get_scoring_percentage(shot_goal_count_dict)

    return tile_state_distribution_dict, tile_pass_distribution_dict, tile_conversion_rate_dict


def compute_xThreat(xThreat: np.ndarray, pitch_graph: Dict[TileID, Tuple[int, int, np.ndarray]]):
    # List[shot, goal, pass_count_surface]
    state_probs_shot_pass, transmission_matrix, state_probs_shot_goal = _get_xThreat_materials(pitch_graph)

    assert xThreat.shape[0] == len(pitch_graph.keys()), "xThreat shape does not match pitch graph key number"

    for tile_id in pitch_graph.keys():
        assert transmission_matrix[tile_id].shape == xThreat.shape, "Transmission matrix does not match xThreat shape"

        pass_payoff = np.sum(transmission_matrix[tile_id] * xThreat)
        pass_value = state_probs_shot_pass[tile_id].pass_prob * pass_payoff

        shot_value = state_probs_shot_pass[tile_id].shot_prob * state_probs_shot_goal[tile_id]

        xThreat[tile_id] = pass_value + shot_value

    return xThreat


# def main():
#     pitch_graph = compute_xThreat(pitch_graph)
#     return pitch_graph

df_all_events = pd.read_csv("2372222_all_events.txt", sep="\t")

initialise_pitch_graph(df_all_events)
