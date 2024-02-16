import os
import csv

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


def read_all_events(game_code, directory):
    """read in all events file and translate metadata back to english"""

    filename = f'{directory}{game_code}_all_events.txt'

    data = []
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='\t')
        header = next(reader)

        translated_header = translate_all_events_meta(header)

        for row in reader:
            row = dict(zip(translated_header, row))
            translated_row = translate_event_type(row)
            data.append(translated_row)
    return data


def translate_event_type(row):
    event_code_classifications = {
        1: "pass",
        2: "offside_pass",
        3: "take_on",
        4: "foul",
        5: "out",
        6: "corner",
        7: "tackle",
        8: "interception",
        9: "turnover",
        10: "save",
        11: "claim",
        12: "clearance",
        13: "miss",
        14: "post",
        15: "attempt_saved",
        16: "goal",
        17: "card",
        18: "player_off",
        19: "player_on",
        20: "player_retired",
        21: "player_returns",
        22: "player_becomes_goalkeeper",
        23: "goalkeeper_becomes_player",
        24: "condition_change",
        25: "official_change",
        27: "start_delay",
        28: "end_delay",
        30: "end",
        32: "start",
        34: "team_setup",
        35: "player_changed_position",
        36: "player_changed_jersey_number",
        37: "collection_end",
        38: "temporary_goal",
        39: "temporary_attempt",
        40: "formation_change",
        41: "punch",
        42: "good_skill",
        43: "deleted_event",
        44: "aerial_duel",
        45: "challenge",
        47: "rescinded_card",
        49: "ball_recovery",
        50: "dispossessed",
        51: "error",
        52: "keeper_pick-up",
        53: "cross_not_claimed",
        54: "smother",
        55: "offside_provoked",
        56: "shield_ball_opponent",
        57: "foul_throw-in",
        58: "penalty_faced",
        59: "keeper_sweeper",
        60: "chance_missed",
        61: "ball_touch",
        63: "temporary_save",
        64: "resume",
        65: "contentious_referee_decision",
        66: "possession_data",
        67: "50/50",
        68: "referee_drop_ball",
        69: "failed_to_block",
        70: "injury_time_announcement",
        71: "coach_setup",
        72: "caught_offside",
        73: "other_ball_contact",
        74: "blocked_pass",
        75: "delayed_start",
        76: "early_end",
        77: "player_off_pitch",
        78: "unidentified",
        79: "unidentified",
        80: "unidentified",
        81: "unidentified",
        82: "unidentified",
        83: "unidentified",
        84: "unidentified",
        85: "unidentified"
    }

    event_code = int(row['event_code'])
    row['event_type'] = event_code_classifications[event_code]
    return row
