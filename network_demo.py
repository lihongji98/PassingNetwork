from db_connect_utils import *
import mongoengine


def main():
    """create pass matrix for home and away team for 11 players who play most minutes"""

    client = db_connect_pymongo()

    match_data = get_match_data("2372355")    

    print(match_data)

    db_disconnect()


def get_match_data(match_code):
    return db.getCollection("match").find({
        'match_id': match_code
        })


if __name__ == "__main__":
    main()

