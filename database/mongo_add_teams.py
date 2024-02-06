import csv
from database import *
import mongoengine
import mongofunctions as mf


def main():
    # password is hardcoded
    mongoengine.connect(host="mongodb+srv://joe:RZqEJSstjBJqglr7@passingnetworks.pyzrvuj.mongodb.net/?retryWrites=true&w=majority")

    games_codes = mf.get_game_codes('c:/Users/joemc/OneDrive/Documents/Football/st_match_report/PassingNetwork/demo_data/')
    
    teams = {}
    for game_code in games_codes:
        teams = add_teams(teams, game_code, 'c:/Users/joemc/OneDrive/Documents/Football/st_match_report/PassingNetwork/demo_data/',)
    team_instances = [Team(team_id=key, team_name=teams[key]) for key in teams.keys()]
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

