import csv
from database import *
import mongoengine
from util import get_game_codes, translate_all_events_meta
from bson import ObjectId

def main():

    mongoengine.connect(db='LaLiga2023', host=)
    
    directory = 'C:/Users/joemc/Documents/UPC_local/PassingNetwork/data/'

    game_codes = get_game_codes(directory)

    competition_id = ObjectId()
    matches = []
    for game_code in game_codes:
        events = read_all_events_first_row(game_code, directory=directory)

        match = {}
        match['match_id'] = events['match_id']
        match['competition_id'] = competition_id
        match = add_home_away_teams(match, game_code, directory=directory)
        matches.append(match)

    match_instances = [Match(**match) for match in matches]
    Match.objects.insert(match_instances, load_bulk=False)


def add_home_away_teams(match_dict, game_code, directory):
    filename = f'{directory}{game_code}_team.txt'

    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='\t')
        header = next(reader)  # Skip the header line
        row = next(reader)
        home_team_id, home_team = row[0], row[1]
        row = next(reader)
        away_team_id, away_team = row[0], row[1]
        match_dict['home_team_id'], match_dict['home_team'] = home_team_id, home_team
        match_dict['away_team_id'], match_dict['away_team'] = away_team_id, away_team

    return match_dict


def read_all_events_first_row(game_code, directory):
    """read in all events file and translate metadata back to english"""

    filename = f'{directory}{game_code}_all_events.txt'

    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='\t')
        header = next(reader)

        translated_header = translate_all_events_meta(header)
        # return first row to get
        row = next(reader)
        events_dict = dict(zip(translated_header, row))

    return events_dict


if __name__ == "__main__":
    main()