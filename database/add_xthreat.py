from bson import ObjectId
import csv
import numpy as np
import mongoengine
import sys
from typing import List

from database.database import Pass
from data_type import PlayerCoordinate
from db_connect_utils import db_connect, db_disconnect
from PitchData import pitch_graph
from xThreat.xThreat import get_tile_id


def add_xthreat():

    db_connect()

    width = 16
    height = 12

    xthreat_matrix : np.ndarray = np.array(get_xthreat('seasonal_xThreat.csv'))
    
    pass_events: List[Pass] = Pass.objects(outcome=1)
    pass_event: Pass
    counter = 0
    total = len(pass_events)
    for pass_event in pass_events:

        origin_pos = PlayerCoordinate(pass_event.origin_pos_x, pass_event.origin_pos_y)
        origin_xthreat: float = xthreat_matrix[get_tile_id(origin_pos)]
        destination_pos = PlayerCoordinate(pass_event.destination_pos_x, pass_event.destination_pos_y)
        destination_xthreat: float = xthreat_matrix[get_tile_id(destination_pos)]

        xthreat = round(max(0, destination_xthreat - origin_xthreat), 3)
        Pass.objects(_id=pass_event._id).update_one(set__xthreat=xthreat)

        counter += 1
        if counter % 1000 == 0:
            print(f'{counter * 100 // total}% Complete')


    db_disconnect()
 

def get_tile_id(player_pos: PlayerCoordinate):
    player_x, player_y = player_pos.x, player_pos.y
    distance_buffer = []
    for tile_id in pitch_graph.nodes:
        center_x = pitch_graph.nodes[tile_id]["pos_info"].center_x
        center_y = pitch_graph.nodes[tile_id]["pos_info"].center_y

        current_distance = np.sqrt((player_x - center_x) ** 2 + (player_y - center_y) ** 2)
        distance_buffer.append([tile_id, current_distance])
    current_tile: int = sorted(distance_buffer, key=lambda x: x[1])[0][0]

    return current_tile


def get_xthreat(path):

    return np.genfromtxt(path)


if __name__ == '__main__':
    add_xthreat()
