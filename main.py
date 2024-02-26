
from db_connect_utils import db_connect, db_disconnect
from MatchRetrieve.match_passing_matrix import MatchPassingMatrix
from Visualisation.network_viz import *
from database.add_all_events import add_all_events
from database.add_passes import add_passes


def main():
        db_connect()
        add_passes()
        db_disconnect()


if __name__ == '__main__':
    main()

