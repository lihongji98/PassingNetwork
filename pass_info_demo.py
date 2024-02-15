from typing import List

from xThreat import xThreat
from db_connect_utils import db_connect, db_disconnect
from database.database import Match, Event
from data_type import PlayerCoordinate


db_connect()

match_demo: Match = Match.objects(home_team="Barcelona", away_team="Athletic Club").first()
match_id = match_demo.match_id

pass_events: List[Event] = Event.objects(match_id=match_id, event_type="pass", outcome=True)
print(len(pass_events))
one_pass: Event
for one_pass in pass_events:
    origin_pos = PlayerCoordinate(one_pass.origin_pos_x, one_pass.origin_pos_y)
    destination_pos = PlayerCoordinate(one_pass.destination_pos_x, one_pass.destination_pos_y)


db_disconnect()

