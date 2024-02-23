from mplsoccer import Pitch
import networkx as nx
from db_connect_utils import db_connect, db_disconnect
from MatchRetrieve.match_passing_matrix import MatchPassingMatrix
import typing
import numpy as np
import matplotlib.pyplot as plt

def get_matrix(match_id="2372355", side='home') -> nx.DiGraph:
    
    passing_matrix = MatchPassingMatrix(match_id=match_id, side=side)

    passingMatrix = passing_matrix.get_pass_count_matrix()
    graph = passing_matrix.home_team_players if side == "home" else passing_matrix.away_team_players

    players = graph.nodes if side == 'home' else graph.nodes

    color = 'b' if side == 'home' else 'r'

    plot_network(graph, players, passingMatrix, color=color)


    return 


def plot_network(graph, players, passingMatrix, color):

    locations = {}
    for player in players:
        locations[player] = graph.nodes(data='average_position')[player]
    
    passers = []
    receivers = []
    for edge in graph.edges:
        passers.append(edge[0])
        receivers.append(edge[1])

    passers_x = []
    passers_y = []
    receivers_x = []
    receivers_y = []
    for i in range(len(graph.edges)):
        passers_x.append(locations[passers[i]].x)
        passers_y.append(locations[passers[i]].y)
        receivers_x.append(locations[receivers[i]].x)
        receivers_y.append(locations[receivers[i]].y)

    # {player_id : norm(received+pass count)}
    
    passing_dict = {list(players)[index]: passing_count for index, passing_count in enumerate(np.sum(passingMatrix, axis=1))}
    receive_dict = {list(players)[index]: receive_count for index, receive_count in enumerate(np.sum(passingMatrix, axis=0))} 
    
    touch_dict = {}
    for player_id in passing_dict.keys():
        touch_count = passing_dict[player_id] + receive_dict[player_id]
        touch_dict[player_id] = touch_count

    max_touches = max(touch_dict.values())
    for player in touch_dict.keys():
        touch_dict[player] = (touch_dict[player] ** 2 / max_touches ** 2) * 2000
    print(touch_dict)

    pitch = Pitch(
    pitch_type="opta", pitch_color="white", line_color="black", linewidth=1,
    )
    fig, axs = pitch.grid(
        figheight=10,
        title_height=0.08,
        endnote_space=0,
        # Turn off the endnote/title axis. I usually do this after
        # I am happy with the chart layout and text placement
        axis=False,
        title_space=0,
        grid_height=0.82,
        endnote_height=0.01,
    )
    fig.set_facecolor("white")
    pass_lines = pitch.lines(
        passers_x,
        passers_y,
        receivers_x,
        receivers_y,
        lw = np.array(list(nx.get_edge_attributes(graph, 'pass_value').values())),
        color = color,
        zorder = 1,
        ax = axs["pitch"],
    )
    pass_nodes = pitch.scatter(
        [pos.x for _, pos in graph.nodes(data='average_position')],
        [pos.y for _, pos in graph.nodes(data='average_position')],
        s= list(touch_dict.values()),
        color=color,
        edgecolors="black",
        linewidth=0.5,
        alpha=1,
        ax=axs["pitch"],
    )
    # pass_nodes_internal = pitch.scatter(
    #     average_locs_and_count.x,
    #     average_locs_and_count.y,
    #     s=average_locs_and_count.marker_size / 2,
    #     color="white",
    #     edgecolors="black",
    #     linewidth=0.5,
    #     alpha=1,
    #     ax=axs["pitch"],
    # )
    # for index, row in average_locs_and_count.iterrows():
    #     text = pitch.annotate(
    #         row.name,
    #         xy=(row.x, row.y),
    #         c="black",
    #         va="center",
    #         ha="center",
    #         size=15,
    #         weight="bold",
    #         ax=axs["pitch"],
    #         fontproperties=oswald_regular.prop,
    #     )
    #     text.set_path_effects([path_effects.withStroke(linewidth=1, foreground="white")])

    # axs["endnote"].text(
    #     1,
    #     1,
    #     "@your_twitter_handle",
    #     color="black",
    #     va="center",
    #     ha="right",
    #     fontsize=15,
    #     fontproperties=oswald_regular.prop,
    # )
    # TITLE_TEXT = f"{TEAM}, {FORMATION} formation"
    # axs["title"].text(
    #     0.5,
    #     0.7,
    #     TITLE_TEXT,
    #     color="black",
    #     va="center",
    #     ha="center",
    #     fontproperties=oswald_regular.prop,
    #     fontsize=30,
    # )
    # axs["title"].text(
    #     0.5,
    #     0.15,
    #     OPPONENT,
    #     color="black",
    #     va="center",
    #     ha="center",
    #     fontproperties=oswald_regular.prop,
    #     fontsize=18,
    # )

    plt.show()