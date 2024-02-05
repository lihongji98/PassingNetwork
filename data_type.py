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
