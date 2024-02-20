
from db_connect_utils import db_connect, db_disconnect
from MatchRetrieve.match_passing_matrix import MatchPassingMatrix


def main():
        db_connect()
        aa = MatchPassingMatrix(match_id="2372355", side="home")
        print(aa.home_team_players.nodes)
        network = aa.get_pass_count_matrix()
        print(network)
        db_disconnect()


if __name__ == '__main__':
    main()

