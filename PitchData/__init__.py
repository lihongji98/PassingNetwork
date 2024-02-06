from typing import Dict

import networkx as nx
import numpy as np
from config import PitchMeta
from data_type import TileVertex, TilePosFeatures, TileStatsFeatures


def find_edges(arr):
    _edges = set()
    height, width = arr.shape

    # Iterate over each element in the array
    for y in range(height):
        for x in range(width):
            current_tile = arr[y, x]

            # Check neighboring tiles
            if x > 0:  # Check left
                _edges.add((current_tile, arr[y, x - 1]))
            if x < width - 1:  # Check right
                _edges.add((current_tile, arr[y, x + 1]))
            if y > 0:  # Check up
                _edges.add((current_tile, arr[y - 1, x]))
            if y < height - 1:  # Check down
                _edges.add((current_tile, arr[y + 1, x]))

    return _edges


X_points = np.linspace(start=0, stop=100, num=PitchMeta.x + 1)
Y_points = np.linspace(start=0, stop=100, num=PitchMeta.y + 1)

total_tile_num = PitchMeta.x * PitchMeta.y

tiles = np.linspace(start=0, stop=total_tile_num - 1, num=total_tile_num, dtype=int).reshape(PitchMeta.y, PitchMeta.x)

tile_pos_info_dict: Dict[int, TilePosFeatures] = {}
tile_stats_info_dict: Dict[int, TileStatsFeatures] = {}
tile_id = 0
for i in range(PitchMeta.y):
    for j in range(PitchMeta.x):
        top_left = TileVertex(np.float32(X_points[j]), np.float32(Y_points[i]))
        bot_right = TileVertex(np.float32(X_points[j + 1]), np.float32(Y_points[i + 1]))
        center_x = (top_left.x + bot_right.x) / 2
        center_y = (top_left.y + bot_right.y) / 2
        tile_pos_features = TilePosFeatures(top_left.x, top_left.y, bot_right.x, bot_right.y, center_x, center_y)

        shot_count, goal_count = 0, 0
        pass_count_surface = np.zeros(shape=(PitchMeta.x * PitchMeta.y))
        tile_stats_features = TileStatsFeatures(shot_count, goal_count, pass_count_surface)
        tile_pos_info_dict[tile_id] = tile_pos_features
        tile_stats_info_dict[tile_id] = tile_stats_features

        tile_id += 1

edges = find_edges(tiles)

pitch_graph = nx.Graph()

for node, pos_features in tile_pos_info_dict.items():
    pitch_graph.add_node(node, pos_info=pos_features)

for node, stats_features in tile_stats_info_dict.items():
    pitch_graph.add_node(node, stats_info=stats_features)

pitch_graph.add_edges_from(edges)
