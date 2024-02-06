import os

def get_game_codes(directory):
    files = os.listdir(directory)

    game_codes = []
    for file in files:
        game_code = file.split('_')[0]
        game_codes.append(game_code)
    game_codes = list(set(game_codes))
    return game_codes
