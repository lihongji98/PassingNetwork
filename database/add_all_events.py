import csv
from database import *
import mongoengine
from util import get_game_codes, translate_all_events_meta, read_all_events, translate_event_type
from db_connect_utils import db_connect, db_disconnect

def main():
    
    db_connect()

    directory = 'C:/Users/joemc/Documents/UPC_local/PassingNetwork/data/'

    games_codes = get_game_codes(directory)

    events = []
    for game_code in games_codes:
        game_events = read_all_events(game_code, directory=directory)
        game_events = add_time(game_code, game_events, directory)
        events.extend(game_events)

    event_instances = [Event(**event) for event in events]
    Event.objects.insert(event_instances, load_bulk=False)

    db_disconnect()


def add_time(game_code, game_events, directory):

    events = read_all_events(game_code, directory)
    period_one_latest_time = 0
    for event in events:
        time = int(event['minute']) * 60 + int(event['second'])
        if event['period'] == '1':
            if time > period_one_latest_time:
                period_one_latest_time = time
    
    for event in game_events:
        if event['period'] == '1':
            event['time'] = int(event['minute']) * 60 + int(event['second'])
        elif event['period'] == '2':
            event['time'] = period_one_latest_time + (int(event['minute']) - 45) * 60 + int(event['second'])

    return game_events

if __name__ == "__main__":
    main()
