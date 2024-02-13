import csv
from database import *
import mongoengine
from util import get_game_codes


def main():
    # password is hardcoded
    mongoengine.connect(db='LaLiga2023', host="")

    directory = 'C:/Users/joemc/Documents/UPC_local/PassingNetwork/data/'

    game_codes = get_game_codes(directory)

    teams = {}
    for game_code in game_codes:
        teams = add_teams(teams, game_code, directory)
    team_instances = [Team(team_id=str(key), team_name=teams[key]) for key in teams.keys()]
    Team.objects.insert(team_instances, load_bulk=False)


def add_teams(teams_dict, game_code, directory):
    filename = f'{directory}{game_code}_team.txt'

    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='\t')
        next(reader)  # Skip the header line
        for row in reader:
            id, name = row
            teams_dict[int(id)] = name
    return teams_dict


if __name__ == "__main__":
    main()
