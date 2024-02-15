from db_connect_utils import *
import pymongo
import pandas as pd


def main():
    """create pass matrix for home and away team for 11 players who play most minutes"""

    db = db_connect_pymongo()
    game_code = "2372355"

    match_data = get_match_data(game_code, db)
    df_match = pd.DataFrame(match_data)
    home_team_id = df_match.at[0, 'home_team_id']
    away_team_id = df_match.at[0, 'away_team_id']
    
    # get start and end time of longest period without substitutions
    for team in [home_team_id, away_team_id]:
        substitutions = get_substitutions(game_code, db, team)
        df_subs = pd.DataFrame(substitutions)

        start_time, end_time = find_longest_period(df_subs)
        
        passes = pd.DataFrame(get_passes(game_code, db, team, start_time, end_time))

        players = passes['origin_player'].unique()
        print(players)
    
    db_disconnect()


def get_passes(game_code, db, team, start_time, end_time):
    return db['pass'].find({
        '$and': [
            {'minute': {'$gt': start_time}},
            {'minute': {'$lt': end_time}}
        ],
        'match_id': game_code,
        'team_id': team
    })


def find_longest_period(df_subs):

    longest_time = 0
    start_time = 0
    end_time = 90 # case with no subs

    minutes = df_subs['minute']
    minutes = [0] + minutes.tolist()

    for i in range(len(minutes) - 1):
        if minutes[i + 1] - minutes[i] > longest_time:
            start_time = minutes[i]
            end_time = minutes[i + 1]
            longest_time = minutes[i + 1] - minutes[i]
        else:
            continue

    return start_time, end_time


def get_substitutions(game_code, db, team):

    return db['event'].find({
        'match_id': game_code,
        'event_code': 18,
        'team_id': team
    })


def get_match_data(game_code, db):

    return db['match'].find({'match_id': game_code})


if __name__ == "__main__":
    main()

