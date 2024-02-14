import csv
from database import *
import mongoengine
from util import get_game_codes


def main():
    
    mongoengine.connect(db='LaLiga2023', host="")

    directory = 'C:/Users/joemc/Documents/UPC_local/PassingNetwork/data/'

    games_codes = get_game_codes(directory)

    passes = []
    for game_code in games_codes:
        game_passes = read_passes(game_code, directory=directory)
        passes.extend(game_passes)

    pass_instances = [Pass(**pass_event) for pass_event in passes]
    Pass.objects.insert(pass_instances, load_bulk=False)



def read_passes(game_code, directory):
    """read in all events file and translate metadata back to english"""

    filename = f'{directory}{game_code}_pass.txt'

    passes = []
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='\t')
        header = next(reader)

        remapped_header = map_passes_meta(header)

        for row in reader:
            row = dict(zip(remapped_header, row))
            passes.append(row)
    return passes


def map_passes_meta(header):
    pass_fields_mapping = {
        'match_id': 'match_id',
        'id': 'pass_id',
        'team_id': 'team_id',
        'period_id': 'period',
        'min': 'minute',
        'sec': 'second',
        'player_id_1': 'origin_player',
        'player_id_2': 'destination_player',
        'outcome': 'outcome',
        'start_x': 'origin_pos_x',
        'start_y': 'origin_pos_y',
        'end_x': 'destination_pos_x',
        'end_y': 'destination_pos_y',
        'offside': 'offside',
        'possession': 'possession',
        'sequence': 'sequence'
    }

    remapped_header = [pass_fields_mapping.get(column, column) for column in header]
    return remapped_header

if __name__ == "__main__":
    main()