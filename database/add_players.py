import csv
from database import *
import mongoengine
from util import get_game_codes


def main():
    mongoengine.connect(db='LaLiga2023', host="")

    directory = 'C:/Users/joemc/Documents/UPC_local/PassingNetwork/data/'

    game_codes = get_game_codes(directory)

    player_data = []
    for game_code in game_codes:
        game_player_data = read_player_data(game_code, directory)
        player_data.extend(game_player_data)

    players = process_player_data(player_data)

    player_instances = [Player(**player) for player in players]
    Player.objects.insert(player_instances, load_bulk=False)


def process_player_data(player_data):
    player_ids = []
    for game_player_data in player_data:
        player_ids.append(game_player_data['id'])
    player_ids = list(set(player_ids))

    players_list = []
    for player_id in player_ids:
        player = {}
        player['player_id'] = player_id

        player['team_id'] = set()
        player['position'] = set()
        player['starts'] = 0
        player['apps'] = 0
        player['minutes'] = 0

        for game_player_data in player_data:
            if game_player_data['id'] == player_id:
                player['first_name'] = game_player_data['first_name']
                player['last_name'] = game_player_data['last_name']
                player['known_name'] = game_player_data['known_name']
                player['team_id'].add(game_player_data['team_id'])
                player['position'].add(game_player_data['position'])
                if game_player_data['start'] == 'Start':
                    player['starts'] += 1
                    player['apps'] += 1
                if game_player_data['start'] == 'Sub' and int(game_player_data['minutes']) > 0:
                    player['apps'] += 1
                player['minutes'] += int(game_player_data['minutes'])

        players_list.append(player)
    return players_list


def read_player_data(game_code, directory):
    filename = f'{directory}{game_code}_player.txt'

    data = []
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='\t')
        header = next(reader)

        translated_header = translate_players_meta(header)

        for row in reader:
            row = dict(zip(translated_header, row))
            data.append(row)
    return data


def translate_players_meta(row):
    english_translations = {
        'id': 'id',
        'first_name': 'first_name',
        'last_name': 'last_name',
        'known_name': 'known_name',
        'team_id': 'team_id',
        'shirt': 'shirt_number',
        'posicion': 'position',
        'titular': 'start',
        'minutos': 'minutes'
    }

    translated_header = [english_translations.get(column, column) for column in row]
    return translated_header


if __name__ == "__main__":
    main()
