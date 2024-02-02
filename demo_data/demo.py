import numpy as np
import pandas as pd
from typing import Dict, Tuple
from data_type import (
    TileID, ConversionRate,
    PlayerCoordinate,
    TileStateCount,
    TileStateDistribution,
    TileShotGoalCount
)


def get_the_closest_tile(player_coordinate: PlayerCoordinate):
    # the pitch size is 100 * 100, and converted to 16 * 12
    player_x, player_y = player_coordinate.x / 100, player_coordinate.y / 100


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


def compute_xThreat(pitch_graph: Dict[TileID, Tuple[int, int, np.ndarray]]):     # List[shot, goal, pass_count_surface]
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


df_all_events = pd.read_csv("2372222_all_events.txt", sep="\t")
pd.set_option('display.max_columns', None)
print(set(df_all_events.tipo.values))
# gol, disparo_parado
# regate_conseguido

df_shot = df_all_events[df_all_events.tipo.isin(["gol", "disparo_parado"])]
df_pass = df_all_events[df_all_events["tipo"] == "pase"]
# df_dribble = df_all_events[df_all_events["tipo"] == "regate_conseguido"]

df_xg = pd.read_csv("2372222_xG_data.txt", sep="\t")
# print(df_shot)


df_key_events = pd.read_csv("2372222_key_event.txt", sep="\t")
print(df_key_events.type.unique())
df_shot_attempt = df_key_events[df_key_events.tipo.isin(["miss", "attempt_saved", "goal"])]
df_goal = df_shot_attempt[df_shot_attempt.type == "goal"]
print()


