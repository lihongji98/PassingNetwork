from mplsoccer import Pitch
import networkx as nx
from db_connect_utils import db_connect, db_disconnect
from MatchRetrieve.match_passing_matrix import MatchPassingMatrix
import typing

def get_matrix(match_id="2372355", side='home') -> nx.DiGraph:
    
    graph = MatchPassingMatrix(match_id=match_id, side=side)

    players = graph.home_team_players.nodes if side == 'home' else graph.away_team_players.nodes

    edges = nx.get_edge_attributes(graph.home_team_players, 'pass_value')

    print(edges)

    
    # passes_between = [[passer.x, passer.y, receiver.x, receiver.y, pass_count]]

    return 


def plot_network(matrix):

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
        passes_between.x,
        passes_between.y,
        passes_between.x_end,
        passes_between.y_end,
        lw=passes_between.width,
        color="#BF616A",
        zorder=1,
        ax=axs["pitch"],
    )
    pass_nodes = pitch.scatter(
        average_locs_and_count.x,
        average_locs_and_count.y,
        s=average_locs_and_count.marker_size,
        color="#BF616A",
        edgecolors="black",
        linewidth=0.5,
        alpha=1,
        ax=axs["pitch"],
    )
    pass_nodes_internal = pitch.scatter(
        average_locs_and_count.x,
        average_locs_and_count.y,
        s=average_locs_and_count.marker_size / 2,
        color="white",
        edgecolors="black",
        linewidth=0.5,
        alpha=1,
        ax=axs["pitch"],
    )
    for index, row in average_locs_and_count.iterrows():
        text = pitch.annotate(
            row.name,
            xy=(row.x, row.y),
            c="black",
            va="center",
            ha="center",
            size=15,
            weight="bold",
            ax=axs["pitch"],
            fontproperties=oswald_regular.prop,
        )
        text.set_path_effects([path_effects.withStroke(linewidth=1, foreground="white")])

    axs["endnote"].text(
        1,
        1,
        "@your_twitter_handle",
        color="black",
        va="center",
        ha="right",
        fontsize=15,
        fontproperties=oswald_regular.prop,
    )
    TITLE_TEXT = f"{TEAM}, {FORMATION} formation"
    axs["title"].text(
        0.5,
        0.7,
        TITLE_TEXT,
        color="black",
        va="center",
        ha="center",
        fontproperties=oswald_regular.prop,
        fontsize=30,
    )
    axs["title"].text(
        0.5,
        0.15,
        OPPONENT,
        color="black",
        va="center",
        ha="center",
        fontproperties=oswald_regular.prop,
        fontsize=18,
    )

    plt.show()