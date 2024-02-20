
from db_connect_utils import db_connect, db_disconnect
from MatchRetrieve.match_passing_matrix import MatchPassingMatrix
from Visualisation.network_viz import *


def main():
        db_connect()
        get_matrix()
        db_disconnect()


if __name__ == '__main__':
    main()

