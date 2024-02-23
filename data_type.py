from typing import TypeAlias
from dataclasses import dataclass
import numpy as np


@dataclass
class PlayerCoordinate:
    x: float
    y: float


@dataclass
class TileStateDistribution:
    """
    shot_prob, pass_prob
    """
    shot_prob: float
    pass_prob: float


@dataclass
class TileStateCount:
    """
    shot_count, pass_count
    """
    shot_count: int
    pass_count: int


@dataclass
class TileShotGoalCount:
    """
    shot_count, goal_count
    """
    shot_count: int
    goal_count: int


TileID: TypeAlias = int
ConversionRate: TypeAlias = float


@dataclass
class TileVertex:
    x: float
    y: float


@dataclass
class TilePosFeatures:
    top_left_x: float
    top_left_y: float
    bot_right_x: float
    bot_right_y: float
    center_x: float
    center_y: float


@dataclass
class TileStatsFeatures:
    shot_count: int
    goal_count: int
    pass_count_surface: np.ndarray


@dataclass
class MatchPlayerEigenvectorCentralityInfo:
    pass_eigenvector_centrality: float
    xthreat_eigenvector_centrality: float
