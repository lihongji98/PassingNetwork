import csv
from database import *
import mongoengine
from util import get_game_codes, translate_all_events_meta

def main():
    # password is hardcoded
    mongoengine.connect(db='LaLiga2023',host="mongodb+srv://joe:RZqEJSstjBJqglr7@passingnetworks.pyzrvuj.mongodb.net/?retryWrites=true&w=majority")

    games_codes = get_game_codes('./data/')

    for game_code in games_codes:
        events = read_all_events(game_code, directory='./data/')
        event_instances = [Event(**event) for event in events]
        Event.objects.insert(event_instances, load_bulk=False)


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
        80: "unidentified",
        83: "unidentified"
    }

    event_code = int(row['event_code'])
    row['event_type'] = event_code_classifications[event_code]
    return row


if __name__ == "__main__":
    main()
