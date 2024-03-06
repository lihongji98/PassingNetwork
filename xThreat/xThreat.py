from typing import Dict
import networkx as nx
import numpy as np

from matplotlib import pyplot as plt

from PitchData import pitch_graph
from config import PitchMeta
from data_type import (
    PlayerCoordinate,
    TileStatsFeatures,
    TileStateDistribution,
    ConversionRate,
    TileID
)
from database.database import Event


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
    """
    The class which contains xThreat information.
    You need to fulfill a team name to get its seasonal xThreat surface.
    If you want to get the overall xThreat surface, just leave it blank.
    """

    def __init__(self, team_name: str = ""):
        self.pitch_graph: nx.Graph = pitch_graph
        self.team_name = team_name
        self.xThreat_surface: np.ndarray = np.zeros(len(self.pitch_graph.nodes))

        self._state_prob_distribution_dict: Dict[TileID, TileStateDistribution] = {}
        self._tile_conversion_dict: Dict[TileID, ConversionRate] = {}
        self._tile_pass_distribution_dict: Dict[TileID, np.ndarray] = {}

    def _fit_retrieve_data(self):
        searching_dict = {'team_name': self.team_name}
        for key, value in searching_dict.copy().items():
            if value == "":
                searching_dict.pop(key)

        print("Reading shot information...")
        shot_info: Event
        shot_event: Event = Event.objects(event_code__in=["13", "14", "15", "16"], **searching_dict)
        for shot_info in shot_event:
            shot_pos = PlayerCoordinate(shot_info.origin_pos_x, shot_info.origin_pos_y)
            tile_id = get_tile_id(shot_pos)
            stats_info: TileStatsFeatures = self.pitch_graph.nodes[tile_id]["stats_info"]
            stats_info.shot_count += 1
        print("the event of shot loaded!")

        print("Reading goal information...")
        goal_info: Event
        goal_event: Event = Event.objects(event_code__in=["16"], **searching_dict)
        for goal_info in goal_event:
            goal_pos = PlayerCoordinate(goal_info.origin_pos_x, goal_info.origin_pos_y)
            tile_id = get_tile_id(goal_pos)
            stats_info: TileStatsFeatures = self.pitch_graph.nodes[tile_id]["stats_info"]
            stats_info.goal_count += 1
        print("the event of goal loaded!")

        print("Reading pass information...")
        pass_info: Event
        pass_event: Event = Event.objects(event_code__in=["1"], **searching_dict, outcome=1)
        for index, pass_info in enumerate(pass_event):
            origin_pos = PlayerCoordinate(pass_info.origin_pos_x, pass_info.origin_pos_y)
            destination_pos = PlayerCoordinate(pass_info.destination_pos_x, pass_info.destination_pos_y)
            origin_tile_id = get_tile_id(origin_pos)
            destination_tile_id = get_tile_id(destination_pos)
            stats_info: TileStatsFeatures = self.pitch_graph.nodes[origin_tile_id]["stats_info"]
            stats_info.pass_count_surface[destination_tile_id] += 1
        print("the event of pass loaded!")

    def _get_state_prob_distribution(self):

        for tile_id in self.pitch_graph.nodes:
            stats_info: TileStatsFeatures = self.pitch_graph.nodes[tile_id]["stats_info"]
            shot_count = stats_info.shot_count
            pass_count = np.sum(stats_info.pass_count_surface)
            shot_pass_sum = shot_count + pass_count

            shot_prob = shot_count / shot_pass_sum if shot_pass_sum > 0 else 0
            pass_prob = pass_count / shot_pass_sum if shot_pass_sum > 0 else 0

            tile_state_prob_distribution = TileStateDistribution(shot_prob, pass_prob)
            self._state_prob_distribution_dict[tile_id] = tile_state_prob_distribution

    def _get_scoring_percentage(self):
        for tile_id in self.pitch_graph.nodes:
            stats_info: TileStatsFeatures = self.pitch_graph.nodes[tile_id]["stats_info"]
            shot_count = stats_info.shot_count
            goal_count = stats_info.goal_count

            conversion_rate = goal_count / shot_count if shot_count > 0 else 0
            self._tile_conversion_dict[tile_id] = conversion_rate

    def _get_pass_distribution(self):

        for tile_id in self.pitch_graph.nodes:
            stats_info: TileStatsFeatures = self.pitch_graph.nodes[tile_id]["stats_info"]
            pass_count_surface = stats_info.pass_count_surface
            total_pass_count = np.sum(pass_count_surface)

            pass_distribution = pass_count_surface / total_pass_count if total_pass_count != 0 \
                else np.zeros_like(pass_count_surface)

            self._tile_pass_distribution_dict[tile_id] = pass_distribution

    def _compute_xThreat(self, _xThreat):
        self._get_state_prob_distribution()
        self._get_scoring_percentage()
        self._get_pass_distribution()

        assert _xThreat.shape[0] == len(self.pitch_graph.nodes), "xThreat shape does not match pitch graph key number"

        current_xThreat = _xThreat.copy()
        for tile_id in self.pitch_graph.nodes:
            assert self._tile_pass_distribution_dict[tile_id].shape == _xThreat.shape, \
                "Transmission matrix does not match xThreat shape"

            pass_payoff = np.sum(self._tile_pass_distribution_dict[tile_id] * current_xThreat)
            pass_value = self._state_prob_distribution_dict[tile_id].pass_prob * pass_payoff
            shot_value = self._state_prob_distribution_dict[tile_id].shot_prob * self._tile_conversion_dict[tile_id]
            _xThreat[tile_id] = pass_value + shot_value

        return _xThreat

    def _train(self, epochs=5):
        for epoch in range(epochs):
            xThreat_buffer = self.xThreat_surface.copy()
            self.xThreat_surface = self._compute_xThreat(self.xThreat_surface)
            xThreat_error = np.sum(xThreat_buffer - self.xThreat_surface)
            print(f"epoch: {epoch+1} -> loss: {abs(xThreat_error)}")
            # if abs(xThreat_error) < 1e-6:
            #     break

        # self.xThreat_surface = np.round(self.xThreat_surface, 1)

    def draw_xThreat_surface(self, train_epoch=5, save=False):
        """
        run this member function to visualize the xThreat surface.
        :param train_epoch: default is 5.
        :param save: True if you want to save the fig
        :return: None
        """
        self._fit_retrieve_data()
        self._train(train_epoch)

        xThreat_surface = self.xThreat_surface.copy().reshape(PitchMeta.y, PitchMeta.x)

        x = np.arange(xThreat_surface.shape[1])
        y = np.arange(xThreat_surface.shape[0])

        Width, Height = np.meshgrid(x, y)

        plt.figure(figsize=(12, 7))
        ax = plt.axes(projection='3d')
        ax.plot_surface(Width, Height, xThreat_surface, rstride=1, cstride=1, cmap='coolwarm', edgecolor='none')
        ax.view_init(35, -200, 0)
        ax.set_zlabel('xThreat', fontsize=10)
        ax.tick_params(axis='z', labelsize=7)

        if save:
            plt.savefig('xThreat_surface_visualization.png', dpi=800)
        plt.show()

    
    def draw_xThreat_surface_2d(self, train_epoch=5, save=False):
        """
        run this member function to visualize the xThreat surface.
        :param train_epoch: default is 5.
        :param save: True if you want to save the fig
        :return: None
        """
        self._fit_retrieve_data()
        self._train(train_epoch)

        xThreat_surface = self.xThreat_surface.copy().reshape(PitchMeta.y, PitchMeta.x)

        x = np.arange(xThreat_surface.shape[1])
        y = np.arange(xThreat_surface.shape[0])

                # Create meshgrid
        X, Y = np.meshgrid(x, y)

        # Plot the 2D heatmap
        plt.figure(figsize=(12, 7))
        plt.imshow(xThreat_surface, cmap='coolwarm', aspect='auto')
        cbar = plt.colorbar(label='xThreat')
        cbar.ax.tick_params(labelsize=12)  # Set font size for color bar labels
        cbar.set_label('xThreat', fontsize=14)
        plt.xlabel('Width', fontsize=16)
        plt.ylabel('Height', fontsize=16)
        plt.title('xThreat Heatmap', fontsize=18)
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        plt.show()

        if save:
            plt.savefig('xThreat_surface_visualization_2d.png', dpi=800)
        plt.show()


    def get_team_xThreat(self, train_epoch=5):
        """
        A training epoch is required to set up, and the default epoch is 5.
        :param train_epoch: default 5
        :return: xThreat surface: np.ndarray with shape 192,
        """
        self._fit_retrieve_data()
        self._train(epochs=train_epoch)

        return self.xThreat_surface


# from db_connect_utils import db_connect, db_disconnect
# db_connect()
# xx = xThreat()
# xThreat = xx.get_team_xThreat(train_epoch=100)
# print(np.round(np.array(xThreat).reshape(12, 16), 1))
# np.savetxt("seasonal_xThreat.csv", xThreat, delimiter=",")
# db_disconnect()
