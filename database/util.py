import os

def get_game_codes(directory):
    files = os.listdir(directory)

    game_codes = []
    for file in files:
        game_code = file.split('_')[0]
        if game_code.isdigit():
            game_codes.append(game_code)
    game_codes = list(set(game_codes))
    return game_codes


def translate_all_events_meta(header):
    english_translations = {
        'codigo': 'event_code',
        'tipo': 'event_type',
        'equipo': 'team_id',
        'player': 'origin_player',
        'x': 'origin_pos_x',
        'y': 'origin_pos_y',
        'min': 'minute',
        'sec': 'second',
        'period': 'period',
        'partido': 'match_id',
        'nombre_equipo': 'team_name',
        'nombre_jugador': 'player_name',
        'outcome': 'outcome',
        'fase': 'pattern_of_play',
        'end_x': 'destination_pos_x',
        'end_y': 'destination_pos_y',
        'extra': 'extra_detail'
    }

    translated_header = [english_translations.get(column, column) for column in header]
    return translated_header